"""Structured decision prompt for one text-interview turn."""

TURN_SCHEMA = {
    "type": "object",
    "properties": {
        "transition": {"type": "string"},
        "decision": {"type": "string", "enum": ["follow_up", "continue"]},
        "follow_up_question": {"type": "string"},
        "assessment": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["needs_development", "developing", "strong"],
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
                "improvements": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["level", "strengths", "improvements"],
            "additionalProperties": False,
        },
    },
    "required": ["transition", "decision", "follow_up_question", "assessment"],
    "additionalProperties": False,
}

SYSTEM_INSTRUCTION = """
You are conducting a supportive but realistic mock interview. Evaluate
only the answer to the current planned question. Do not make a hiring decision and
do not mention scores or private assessment. The transition must be one brief,
neutral, professional sentence; do not coach during the interview.

Choose follow_up only when clarification or one concrete example would materially
improve the evidence, and only when a follow-up is allowed. Otherwise continue.
When continuing, follow_up_question must be an empty string. Never ask for protected
or sensitive personal information. Do not invent candidate facts.
""".strip()


def build_turn_prompt(*, question: dict, answers: list[str], follow_up_allowed: bool) -> str:
    import json

    return f"""
PLANNED QUESTION AND PRIVATE RUBRIC:
{json.dumps(question, ensure_ascii=False)}

CANDIDATE ANSWER(S) TO THIS QUESTION:
{json.dumps(answers, ensure_ascii=False)}

FOLLOW-UP ALLOWED: {str(follow_up_allowed).lower()}

Return a private assessment and decide whether one follow-up is necessary.
""".strip()
