"""Prompt and schema for building a structured, hidden interview plan."""

INTERVIEW_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "opening_message": {"type": "string"},
        "estimated_minutes": {"type": "integer", "minimum": 5, "maximum": 10},
        "competencies": {
            "type": "array",
            "minItems": 3,
            "maxItems": 8,
            "items": {"type": "string"},
        },
        "questions": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "competency": {"type": "string"},
                    "purpose": {"type": "string"},
                    "evidence_source": {
                        "type": "string",
                        "enum": [
                            "resume",
                            "job_description",
                            "student_provided_context",
                            "general_role_expectation",
                        ],
                    },
                    "follow_up_if_shallow": {"type": "string"},
                    "follow_up_if_strong": {"type": "string"},
                    "rubric": {
                        "type": "object",
                        "properties": {
                            "strong_answer": {"type": "string"},
                            "developing_answer": {"type": "string"},
                            "warning_sign": {"type": "string"},
                        },
                        "required": [
                            "strong_answer",
                            "developing_answer",
                            "warning_sign",
                        ],
                        "additionalProperties": False,
                    },
                },
                "required": [
                    "question",
                    "competency",
                    "purpose",
                    "evidence_source",
                    "follow_up_if_shallow",
                    "follow_up_if_strong",
                    "rubric",
                ],
                "additionalProperties": False,
            },
        },
        "closing_message": {"type": "string"},
    },
    "required": [
        "opening_message",
        "estimated_minutes",
        "competencies",
        "questions",
        "closing_message",
    ],
    "additionalProperties": False,
}

SYSTEM_INSTRUCTION = """
You design realistic, fair practice interviews for university students. Build an
interview plan, not a hiring recommendation. Ask one primary question at a time.
Questions must fit the selected interview round: recruiter screens emphasize
motivation and communication; hiring managers emphasize role fit and judgment;
technical specialists probe role-relevant knowledge; panels combine perspectives.

Ground personalized questions in the supplied evidence. Never invent candidate
experience. Student-provided context may guide a question but is not resume evidence.
Never say or imply that the candidate used a tool, method, or skill unless the resume
or student-provided context explicitly says so. When a preferred job skill is absent,
state that it is listed by the role and ask about transferable experience or how the
candidate would learn it. For example, do not say "You mentioned using Tableau" when
only the job description mentions Tableau.
Avoid protected characteristics and sensitive personal information. Do not require
knowledge that is absent from the job description unless it is a reasonable general
expectation for the named role. Use behavioral, situational, and technical questions
in proportions appropriate to the round. Do not ask trick questions.

The rubric is coaching guidance, not an automated hiring score. A warning sign means
an answer needs clarification or development; it must not make a hiring decision.

Every interview must begin with exactly one concise introductory question inviting
the candidate to summarize their background and interest in the role in about 60-90
seconds. Adapt its emphasis to the round: motivation and direction for recruiter/HR,
role connection for a hiring manager, relevant technical preparation for a technical
specialist, and overall value for a panel/final round. In a full interview loop, ask
this introduction only once at the beginning and do not repeat it in later stages.
""".strip()


def build_interview_plan_prompt(
    *,
    job_title: str,
    company: str,
    interview_round: str,
    challenge_level: str,
    interview_minutes: int,
    profile: dict,
    student_context: dict[str, str],
) -> str:
    import json

    public_profile = {key: value for key, value in profile.items() if not key.startswith("_")}
    return f"""
Create a mock interview plan sized for the selected interview length.

JOB TITLE: {job_title}
EMPLOYER: {company or "Not provided"}
INTERVIEW ROUND: {interview_round}
CHALLENGE LEVEL: {challenge_level}
TARGET INTERVIEW LENGTH: {interview_minutes} minutes

EVIDENCE-GROUNDED PROFILE:
{json.dumps(public_profile, ensure_ascii=False)}

OPTIONAL STUDENT-PROVIDED CONTEXT (not resume evidence):
{json.dumps(student_context, ensure_ascii=False) if student_context else "None provided"}

Plan the question count for the selected length: 2-3 primary questions for 5 minutes
and 3-4 for 10 minutes. Set estimated_minutes to exactly the selected target length.
The first question must be the round-appropriate introduction described
in the system instruction. Order the remaining questions naturally from broad context
to deeper role-specific assessment.
Use follow-ups only when useful; the live interviewer will choose them based on the
student's answer. Do not include feedback in the opening or reveal the rubric.
""".strip()
