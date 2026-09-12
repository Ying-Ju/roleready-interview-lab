"""Replaceable model adapter for resume and job-description analysis."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from google import genai
from google.genai import errors, types

from prompts.profile import PROFILE_SCHEMA, SYSTEM_INSTRUCTION, build_profile_prompt


DEFAULT_TEXT_MODEL = "gemini-3.7-flash"
FALLBACK_TEXT_MODELS = ("gemini-3.6-flash", "gemini-3.5-flash-lite")


class ProfileAnalysisUnavailable(RuntimeError):
    """Raised when all free-tier model choices are temporarily unavailable."""


def configured_api_key() -> str:
    """Return the Gemini key from the process environment, if configured."""
    return os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()


def analyze_interview_profile(
    *,
    api_key: str,
    job_title: str,
    company: str,
    interview_round: str,
    challenge_level: str,
    resume_text: str,
    job_description: str,
) -> dict[str, Any]:
    """Generate a structured profile using Gemini's free-tier-compatible API."""
    client = genai.Client(api_key=api_key)
    prompt = build_profile_prompt(
        job_title=job_title,
        company=company,
        interview_round=interview_round,
        challenge_level=challenge_level,
        resume_text=resume_text,
        job_description=job_description,
    )
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.15,
        response_mime_type="application/json",
        response_json_schema=PROFILE_SCHEMA,
    )

    preferred_model = os.getenv("FLYER_TEXT_MODEL", DEFAULT_TEXT_MODEL).strip()
    models = tuple(dict.fromkeys((preferred_model, *FALLBACK_TEXT_MODELS)))
    last_error: Exception | None = None
    for model in models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                if not response.text:
                    raise RuntimeError("The model returned an empty profile.")
                profile = json.loads(response.text)
                profile["_model_used"] = model
                return profile
            except errors.ServerError as exc:
                last_error = exc
                if getattr(exc, "code", None) != 503:
                    raise
                if attempt == 0:
                    time.sleep(1.5)
            except errors.ClientError as exc:
                last_error = exc
                if getattr(exc, "code", None) in (404, 429):
                    break
                raise

    raise ProfileAnalysisUnavailable(
        "The available free Gemini models are busy or have reached today's quota. "
        "Your uploaded files are still available; please try again later."
    ) from last_error
