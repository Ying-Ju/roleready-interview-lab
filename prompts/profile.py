"""Prompts and schema for evidence-grounded interview profile analysis."""

PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_summary": {"type": "string"},
        "education_and_focus": {"type": "array", "items": {"type": "string"}},
        "relevant_experience": {"type": "array", "items": {"type": "string"}},
        "demonstrated_skills": {"type": "array", "items": {"type": "string"}},
        "role_priorities": {"type": "array", "items": {"type": "string"}},
        "strong_matches": {"type": "array", "items": {"type": "string"}},
        "topics_to_verify": {"type": "array", "items": {"type": "string"}},
        "interview_focus": {"type": "array", "items": {"type": "string"}},
        "clarifying_questions": {
            "type": "array",
            "minItems": 0,
            "maxItems": 4,
            "items": {"type": "string"},
        },
    },
    "required": [
        "candidate_summary",
        "education_and_focus",
        "relevant_experience",
        "demonstrated_skills",
        "role_priorities",
        "strong_matches",
        "topics_to_verify",
        "interview_focus",
        "clarifying_questions",
    ],
    "additionalProperties": False,
}

SYSTEM_INSTRUCTION = """
You prepare fair, evidence-grounded job interview practice for candidates using a
university-provided practice tool.
Use only the supplied resume and job description. Never infer protected traits,
personality, or facts that are not stated. Do not reproduce or discuss contact
details, street addresses, student IDs, or other identifying information.

Do not assume that a candidate is entry-level, inexperienced, or pursuing their first
career merely because they are a student or have a recent education entry. Candidates
may have internships in different industries, substantial prior employment, military
or community experience, management responsibility, or may be experienced professionals
returning to school. Describe career background and readiness only from evidence in the
resume and job description. A major, degree, or course title alone does not prove a
skill or determine career stage.

Distinguish demonstrated evidence from claims that should be verified in an
interview. Treat missing information as unknown, not as a deficiency. Phrase gaps
as neutral "topics to verify." Keep the analysis concise and useful to the student.

If the documents lack important background needed to tailor the interview, provide
2-4 concise clarifying questions. Ask only about high-value information not already
answered by the resume. If the documents are already sufficient, return an empty
clarifying_questions list. Do not ask for contact, demographic, medical, financial,
or other sensitive personal information.
""".strip()


def build_profile_prompt(
    *,
    job_title: str,
    company: str,
    interview_round: str,
    challenge_level: str,
    resume_text: str,
    job_description: str,
) -> str:
    return f"""
Create an interview preparation profile for the following application.

JOB TITLE: {job_title}
EMPLOYER: {company or "Not provided"}
INTERVIEW ROUND: {interview_round}
CHALLENGE LEVEL: {challenge_level}

RESUME:
<resume>
{resume_text}
</resume>

JOB DESCRIPTION:
<job_description>
{job_description}
</job_description>

For demonstrated skills and strong matches, describe the evidence briefly.
For interview focus, account for the selected interview round and challenge level.
Do not include interview questions yet.
""".strip()
