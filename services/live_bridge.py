"""Bidirectional Streamlit wrapper for the live interview frontend."""

import base64
from functools import lru_cache
from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

from services.interviewer_personas import persona_details

_component = components.declare_component(
    "flyer_live_interview",
    path=str(Path(__file__).resolve().parent.parent / "live_component_frontend"),
)

_AVATAR_DIR = Path(__file__).resolve().parent.parent / "assets" / "interviewers" / "production"
@lru_cache(maxsize=4)
def _avatar_data_uri(filename: str) -> str:
    encoded = base64.b64encode((_AVATAR_DIR / filename).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def live_interview_component(
    *, token: str, model: str, voice: str, interviewer_persona: str,
    duration_minutes: int = 10, interviewer_label: str = "",
    key: str = "live_interview"
) -> dict[str, Any] | None:
    avatar_file = persona_details(interviewer_persona)["filename"]
    avatar_role = interviewer_label.strip() or "Interviewer"
    return _component(
        token=token,
        model=model,
        voice=voice,
        durationMinutes=max(1, min(int(duration_minutes), 10)),
        avatarDataUri=_avatar_data_uri(avatar_file),
        avatarRole=avatar_role,
        key=key,
        default=None,
    )
