"""Structured, evidence-grounded interview feedback prompt."""

FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "strengths": {
            "type": "array", "minItems": 1, "maxItems": 4,
            "items": {"type": "object", "properties": {
                "observation": {"type": "string"}, "evidence": {"type": "string"}},
                "required": ["observation", "evidence"], "additionalProperties": False},
        },
        "improvements": {
            "type": "array", "minItems": 1, "maxItems": 4,
            "items": {"type": "object", "properties": {
                "observation": {"type": "string"}, "evidence": {"type": "string"},
                "next_step": {"type": "string"}},
                "required": ["observation", "evidence", "next_step"],
                "additionalProperties": False},
        },
        "communication": {"type": "string"},
        "role_alignment": {"type": "string"},
        "next_practice_focus": {"type": "array", "minItems": 2, "maxItems": 4,
                                "items": {"type": "string"}},
    },
    "required": ["summary", "strengths", "improvements", "communication",
                 "role_alignment", "next_practice_focus"],
    "additionalProperties": False,
}

SYSTEM_INSTRUCTION = """
You are a supportive university career coach. Evaluate only what the candidate
actually said in the supplied transcript. Do not infer ability, experience, tone,
confidence, body language, or speaking pace when the transcript does not establish
it. Do not make a hiring recommendation or assign a numerical score. Give concise,
specific, actionable feedback appropriate to the candidate's evidenced background and
the target role. Do not assume the candidate is entry-level because they use a university
service. Evidence must be a short paraphrase, not a fabricated quotation. If the
transcript is incomplete, say so and limit the conclusions accordingly.
""".strip()


def build_feedback_prompt(*, setup: dict, profile: dict, transcript: list[dict]) -> str:
    import json

    public_profile = {k: v for k, v in profile.items() if not k.startswith("_")}
    return f"""
Review this mock interview.

INTERVIEW SETUP:
{json.dumps({k: setup.get(k) for k in ('job_title', 'company', 'interview_round', 'challenge_level')}, ensure_ascii=False)}

ROLE/CANDIDATE CONTEXT:
{json.dumps(public_profile, ensure_ascii=False)}

TRANSCRIPT:
{json.dumps(transcript, ensure_ascii=False)}

Focus on clarity, specificity, relevance, use of examples, and connection to the
role. Treat transcription errors cautiously. Return the requested structured feedback.
""".strip()
