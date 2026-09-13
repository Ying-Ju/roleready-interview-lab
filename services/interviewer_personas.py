"""Interviewer appearance and voice pairings independent of interview role."""

from __future__ import annotations

import secrets


# Filenames remain stable so the final commissioned artwork can replace the
# provisional images without changing application code. Persona selection is
# deliberately random and never uses candidate data.
INTERVIEWER_PERSONAS = {
    "persona_1": {"filename": "recruiter.png", "voice": "Aoede"},
    "persona_2": {"filename": "hiring_manager.png", "voice": "Charon"},
    "persona_3": {"filename": "technical_interviewer.png", "voice": "Iapetus"},
    "persona_4": {"filename": "panel_chair.png", "voice": "Kore"},
}


def choose_interviewer_persona() -> str:
    """Choose an interviewer without considering any candidate attributes."""
    return secrets.choice(tuple(INTERVIEWER_PERSONAS))


def persona_details(persona: str) -> dict[str, str]:
    """Return a valid appearance/voice pairing for a stored persona key."""
    return INTERVIEWER_PERSONAS.get(persona, INTERVIEWER_PERSONAS["persona_2"])
