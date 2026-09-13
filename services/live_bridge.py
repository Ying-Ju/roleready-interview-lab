"""Bidirectional Streamlit wrapper for the live interview frontend."""

import base64
from functools import lru_cache
from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_component = components.declare_component(
    "flyer_live_interview",
    path=str(Path(__file__).resolve().parent.parent / "live_component_frontend"),
)

_AVATAR_DIR = Path(__file__).resolve().parent.parent / "assets" / "interviewers" / "production"
_ROUND_AVATARS = {
    "Recruiter / HR screen": ("recruiter.png", "Recruiter"),
    "Hiring manager": ("hiring_manager.png", "Hiring Manager"),
    "Technical specialist": ("technical_interviewer.png", "Technical Interviewer"),
    "Panel / final interview": ("panel_chair.png", "Panel Chair"),
    "Full interview loop": ("hiring_manager.png", "Lead Interviewer"),
}


@lru_cache(maxsize=4)
def _avatar_data_uri(filename: str) -> str:
    encoded = base64.b64encode((_AVATAR_DIR / filename).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def live_interview_component(
    *, token: str, model: str, voice: str, interview_round: str,
    duration_minutes: int = 10, interviewer_label: str = "",
    key: str = "live_interview"
) -> dict[str, Any] | None:
    avatar_file, avatar_role = _ROUND_AVATARS.get(
        interview_round, _ROUND_AVATARS["Hiring manager"]
    )
    avatar_role = interviewer_label.strip() or avatar_role
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
