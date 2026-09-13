"""Provider-isolated text interview turn evaluation."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from google import genai
from google.genai import errors, types

from prompts.interview_turn import SYSTEM_INSTRUCTION, TURN_SCHEMA, build_turn_prompt
from services.profile_analyzer import (
    DEFAULT_TEXT_MODEL,
    FALLBACK_TEXT_MODELS,
    ProfileAnalysisUnavailable,
)


def evaluate_answer(
    *, api_key: str, question: dict[str, Any], answers: list[str], follow_up_allowed: bool
) -> dict[str, Any]:
    """Evaluate one answer privately and choose whether to ask a follow-up."""
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
        response_mime_type="application/json",
        response_json_schema=TURN_SCHEMA,
    )
    models = tuple(
        dict.fromkeys(
            (os.getenv(
                "ROLEREADY_TEXT_MODEL", os.getenv("FLYER_TEXT_MODEL", DEFAULT_TEXT_MODEL)
            ).strip(), *FALLBACK_TEXT_MODELS)
        )
    )
    last_error: Exception | None = None
    for model in models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=build_turn_prompt(
                        question=question,
                        answers=answers,
                        follow_up_allowed=follow_up_allowed,
                    ),
                    config=config,
                )
                if not response.text:
                    raise RuntimeError("The interviewer returned an empty response.")
                result = json.loads(response.text)
                result["_model_used"] = model
                return result
            except errors.ServerError as exc:
                last_error = exc
                if getattr(exc, "code", None) != 503:
                    raise
                if attempt == 0:
                    time.sleep(1.0)
            except errors.ClientError as exc:
                last_error = exc
                if getattr(exc, "code", None) in (404, 429):
                    break
                raise
    raise ProfileAnalysisUnavailable(
        "The available free interview models are busy or have reached today's "
        "quota. Your answer was not lost; copy it below and try again later."
    ) from last_error
