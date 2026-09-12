"""Gemini-backed interview plan generation."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from google import genai
from google.genai import errors, types

from prompts.interview_plan import (
    INTERVIEW_PLAN_SCHEMA,
    SYSTEM_INSTRUCTION,
    build_interview_plan_prompt,
)
from services.profile_analyzer import (
    DEFAULT_TEXT_MODEL,
    FALLBACK_TEXT_MODELS,
    ProfileAnalysisUnavailable,
)


def generate_interview_plan(
    *,
    api_key: str,
    job_title: str,
    company: str,
    interview_round: str,
    challenge_level: str,
    interview_minutes: int,
    profile: dict[str, Any],
    student_context: dict[str, str],
) -> dict[str, Any]:
    """Create a hidden, structured plan for the live interview."""
    client = genai.Client(api_key=api_key)
    prompt = build_interview_plan_prompt(
        job_title=job_title,
        company=company,
        interview_round=interview_round,
        challenge_level=challenge_level,
        interview_minutes=interview_minutes,
        profile=profile,
        student_context=student_context,
    )
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.35,
        response_mime_type="application/json",
        response_json_schema=INTERVIEW_PLAN_SCHEMA,
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
                    raise RuntimeError("The model returned an empty interview plan.")
                plan = json.loads(response.text)
                plan["_model_used"] = model
                return plan
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
        "Your profile is still available; please try again later."
    ) from last_error
