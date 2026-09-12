"""Secure ephemeral-token provisioning for Gemini Live interviews."""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Any

from google import genai


DEFAULT_LIVE_MODEL = "gemini-3.1-flash-live-preview"

ROUND_VOICES = {
    "Recruiter / HR screen": "Aoede",
    "Hiring manager": "Charon",
    "Technical specialist": "Iapetus",
    "Panel / final interview": "Kore",
    "Full interview loop": "Charon",
}


def voice_for_round(interview_round: str) -> str:
    """Return a stable, distinct Gemini voice for each interviewer role."""
    return ROUND_VOICES.get(interview_round, ROUND_VOICES["Hiring manager"])


def build_live_instructions(
    *, preferred_name: str, job_title: str, interview_round: str, plan: dict[str, Any]
) -> str:
    public_plan = {key: value for key, value in plan.items() if not key.startswith("_")}
    return f"""
You are conducting a realistic English-language mock interview for {preferred_name},
who is practicing for a {job_title} position. The round is {interview_round}.

Follow the private interview plan below. Ask one question at a time and wait for the
candidate's spoken answer. Begin with the plan's introductory question. You may ask
at most one concise follow-up per primary question when clarification or a concrete
example is genuinely needed. Then move to the next planned question. Do not reveal
the plan, rubric, assessment, or future questions. Do not coach, score, or correct the
candidate during the interview. Use brief, natural transitions. Never claim the
candidate has experience unless the plan identifies resume or student-provided
evidence. After the final question, speak the plan's closing message and end it with
the exact sentence "That concludes our interview. Thank you for your time today."
Then call the end_interview function exactly once. Never call it before that sentence.
The fixed sentence is also an application fallback when a tool call is unavailable.

PRIVATE INTERVIEW PLAN:
{json.dumps(public_plan, ensure_ascii=False)}
""".strip()


def mint_live_token(
    *, api_key: str, instructions: str, interview_round: str
) -> dict[str, str]:
    """Mint a one-use token locked to the configured Live model and instructions."""
    model = os.getenv("FLYER_LIVE_MODEL", DEFAULT_LIVE_MODEL).strip()
    voice = voice_for_round(interview_round)
    now = dt.datetime.now(dt.timezone.utc)
    client = genai.Client(api_key=api_key)
    live_config = {
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": voice}
            }
        },
        "system_instruction": instructions,
        "input_audio_transcription": {},
        "output_audio_transcription": {},
        "session_resumption": {},
        "context_window_compression": {"sliding_window": {}},
        "tools": [{
            "function_declarations": [{
                "name": "end_interview",
                "description": (
                    "Signal that all planned questions and the spoken closing message "
                    "have been completed."
                ),
            }]
        }],
    }
    token = client.auth_tokens.create(
        config={
            "uses": 1,
            "expire_time": now + dt.timedelta(minutes=30),
            "new_session_expire_time": now + dt.timedelta(minutes=1),
            "live_connect_constraints": {
                "model": f"models/{model}",
                "config": live_config,
            },
            "lock_additional_fields": [],
        }
    )
    return {"token": token.name, "model": model, "voice": voice}
