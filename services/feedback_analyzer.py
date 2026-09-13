"""Generate post-interview coaching feedback with Gemini."""

import json
import os
import time
from typing import Any

from google import genai
from google.genai import errors, types

from prompts.feedback import FEEDBACK_SCHEMA, SYSTEM_INSTRUCTION, build_feedback_prompt
from services.profile_analyzer import DEFAULT_TEXT_MODEL, FALLBACK_TEXT_MODELS, ProfileAnalysisUnavailable


def generate_feedback(*, api_key: str, setup: dict, profile: dict,
                      transcript: list[dict]) -> dict[str, Any]:
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.25,
        response_mime_type="application/json",
        response_json_schema=FEEDBACK_SCHEMA,
    )
    models = tuple(dict.fromkeys((os.getenv(
        "ROLEREADY_TEXT_MODEL", os.getenv("FLYER_TEXT_MODEL", DEFAULT_TEXT_MODEL)
    ).strip(),
                                  *FALLBACK_TEXT_MODELS)))
    last_error: Exception | None = None
    for model in models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=build_feedback_prompt(
                        setup=setup, profile=profile, transcript=transcript
                    ),
                    config=config,
                )
                if not response.text:
                    raise RuntimeError("The model returned empty feedback.")
                result = json.loads(response.text)
                result["_model_used"] = model
                return result
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
        "The available Gemini models are busy or have reached the current quota. "
        "Your transcript is still available; please try generating feedback later."
    ) from last_error
