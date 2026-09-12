"""Flyer Interview Lab — standalone Streamlit entry point."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load local development secrets from this app's directory. Existing operating
# system environment variables take precedence over values in the file.
load_dotenv(Path(__file__).with_name(".env"))

from services.document_parser import (
    DocumentParseError,
    extract_document_text,
    redact_contact_details,
)
from services.feedback_analyzer import generate_feedback
from services.interview_planner import generate_interview_plan
from services.live_bridge import live_interview_component
from services.live_interview import build_live_instructions, mint_live_token
from services.pdf_report import create_feedback_pdf
from services.profile_analyzer import (
    ProfileAnalysisUnavailable,
    analyze_interview_profile,
    configured_api_key,
)
from services.text_interview import evaluate_answer


APP_NAME = "Flyer Interview Lab"
ALLOWED_EMAIL_DOMAIN = "udayton.edu"
DEV_MODE_ENV_VAR = "FLYER_DEV_MODE"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def auth_is_configured() -> bool:
    """Return whether Streamlit OIDC settings are available."""
    try:
        return "auth" in st.secrets
    except (FileNotFoundError, KeyError):
        return False


def dev_mode_enabled() -> bool:
    """Allow an explicit local-only authentication bypass during development."""
    return os.getenv(DEV_MODE_ENV_VAR, "").strip().lower() in {"1", "true", "yes"}


def google_api_key() -> str:
    """Read the Gemini key from the environment or Streamlit secrets."""
    api_key = configured_api_key()
    if api_key:
        return api_key
    try:
        return str(st.secrets.get("GOOGLE_API_KEY", "")).strip()
    except FileNotFoundError:
        return ""


def clear_practice_data() -> None:
    """Remove uploaded documents and practice context from this Streamlit session."""
    for key in list(st.session_state):
        del st.session_state[key]


def logout_and_clear() -> None:
    """Clear in-memory practice data before ending an authenticated session."""
    clear_practice_data()
    st.logout()


def login_page() -> None:
    """Render the public introduction and UD sign-in screen."""
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="stAppViewContainer"] { background: #f6f7fa; }
        .block-container {
            max-width: 1120px;
            padding-top: 3rem;
            padding-bottom: 2rem;
        }
        .fil-shell {
            overflow: hidden;
            background: #ffffff;
            border: 1px solid #e0e4eb;
            border-radius: 18px;
            box-shadow: 0 18px 45px rgba(20, 35, 60, 0.11);
        }
        .fil-accent {
            height: 7px;
            background: linear-gradient(90deg, #ce1141 0 78%, #004b87 78%);
        }
        .fil-main {
            display: grid;
            grid-template-columns: 1.35fr 0.75fr;
            gap: 42px;
            padding: 48px;
        }
        .fil-eyebrow {
            margin: 0 0 13px;
            color: #ce1141;
            font-size: 0.9rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }
        .fil-title {
            max-width: 600px;
            margin: 0;
            color: #172033;
            font-size: clamp(2rem, 4vw, 3.25rem);
            font-weight: 650;
            line-height: 1.12;
        }
        .fil-lead {
            max-width: 620px;
            margin: 18px 0 27px;
            color: #526279;
            font-size: 1.15rem;
            line-height: 1.65;
        }
        .fil-steps {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
        }
        .fil-step {
            padding-top: 14px;
            border-top: 2px solid #e5e9f0;
        }
        .fil-step-number {
            color: #ce1141;
            font-size: 0.88rem;
            font-weight: 650;
        }
        .fil-step strong {
            display: block;
            margin: 7px 0 5px;
            color: #172033;
            font-size: 1rem;
        }
        .fil-step span:last-child {
            color: #637188;
            font-size: 0.92rem;
            line-height: 1.55;
        }
        .fil-signin {
            align-self: center;
            overflow: hidden;
            background: #f7f8fb;
            border: 1px solid #e0e4eb;
            border-radius: 14px;
        }
        .fil-signin-copy {
            margin: 0;
            padding: 24px 24px 4px;
            color: #172033;
            font-size: 1.12rem;
            font-weight: 650;
        }
        .fil-signin-subcopy {
            margin: 0;
            padding: 0 24px 10px;
            color: #637188;
            font-size: 0.84rem;
            line-height: 1.5;
        }
        .fil-notes {
            padding: 2px 24px 22px;
            color: #637188;
            font-size: 0.74rem;
            line-height: 1.5;
        }
        .fil-note {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e1e5ec;
        }
        .fil-footer {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            flex-wrap: wrap;
            padding: 14px 48px;
            color: #69768a;
            background: #eef1f5;
            font-size: 0.84rem;
        }
        [data-testid="stCaptionContainer"] p {
            font-size: 0.92rem;
            line-height: 1.55;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            border-color: #ce1141;
            background: #ce1141;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            border-color: #a6192e;
            background: #a6192e;
        }
        @media (max-width: 760px) {
            .block-container { padding: 1.25rem 0.75rem; }
            .fil-main { grid-template-columns: 1fr; gap: 26px; padding: 28px; }
            .fil-steps { grid-template-columns: 1fr; }
            .fil-footer { padding: 14px 28px; }
        }
        </style>

        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="fil-accent"></div>', unsafe_allow_html=True)
        intro_col, login_col = st.columns([1.45, 0.75], gap="large")
        with intro_col:
            st.markdown(
                """
                <p class="fil-eyebrow">Department of Mathematics · University of Dayton</p>
                <h1 class="fil-title">Practice the interview you are actually preparing for.</h1>
                <p class="fil-lead">
                  Flyer Interview Lab creates a realistic mock interview from your résumé,
                  the job description, and the interview round—then gives you focused
                  feedback to improve your next attempt.
                </p>
                <div class="fil-steps">
                  <div class="fil-step"><span class="fil-step-number">01</span><strong>Provide context</strong><span>Upload your résumé and job description, then enter the job title.</span></div>
                  <div class="fil-step"><span class="fil-step-number">02</span><strong>Practice aloud</strong><span>Respond to role-specific questions from the appropriate interviewer.</span></div>
                  <div class="fil-step"><span class="fil-step-number">03</span><strong>Review feedback</strong><span>See strengths, gaps, suggested improvements, and next steps.</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with login_col:
            with st.container(border=True):
                st.markdown("### Ready to practice?")
                st.caption("Use your University of Dayton account to continue.")
                if st.button("Sign in with UD", type="primary", use_container_width=True):
                    if auth_is_configured():
                        st.login()
                    else:
                        st.warning(
                            "UD sign-in is not configured yet. "
                            "Add the OIDC settings to Streamlit secrets."
                        )
                st.caption(
                    "Access is limited to authenticated @udayton.edu accounts."
                )
                st.caption(
                    "Uploaded materials tailor the practice session. Do not upload "
                    "documents containing sensitive personal information."
                )

        st.markdown(
            '<footer class="fil-footer"><span>Flyer Interview Lab</span>'
            '<span>Developed by Tessa</span></footer>',
            unsafe_allow_html=True,
        )


def user_is_allowed() -> bool:
    """Allow authenticated University of Dayton accounts."""
    if not getattr(st.user, "is_logged_in", False):
        return False
    email = str(st.user.get("email", "")).strip().lower()
    return email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}")


def setup_page() -> None:
    """Collect the minimum context required for a tailored interview."""
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background: #f6f7fa; }
        .block-container { max-width: 1080px; padding-top: 2rem; }
        .setup-kicker {
            color: #ce1141;
            font-size: 0.9rem;
            font-weight: 650;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .setup-title { margin: 0.15rem 0 0.45rem; color: #172033; }
        .setup-copy { color: #526279; font-size: 1.05rem; line-height: 1.55; }
        .setup-section {
            margin: 1.3rem 0 0.7rem;
            padding: 0.85rem 1rem;
            color: #172033;
            background: linear-gradient(90deg, #fff3f6, #ffffff);
            border-left: 5px solid #ce1141;
            border-radius: 0 10px 10px 0;
            font-size: 1.15rem;
            font-weight: 700;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            color: #172033;
            background: #ffffff;
            border: 2px solid #9da9b8;
            border-radius: 8px;
        }
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stTextArea"] textarea:hover {
            border-color: #526279;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ce1141;
            box-shadow: 0 0 0 1px #ce1141;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: #ffffff;
            border: 2px dashed #9da9b8;
        }
        div[data-testid="stForm"] {
            padding: 1.4rem 1.6rem 1.6rem;
            background: #ffffff;
            border: 1px solid #dbe0e8;
            border-radius: 14px;
            box-shadow: 0 8px 24px rgba(20, 35, 60, 0.07);
        }
        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
            border-color: #ce1141;
            background: #ce1141;
        }
        </style>
        <p class="setup-kicker">Flyer Interview Lab</p>
        <h1 class="setup-title">Prepare your mock interview</h1>
        <p class="setup-copy">
          Provide the position and application materials you are actually using.
          The interviewer will tailor questions to your background and the employer's needs.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("interview_setup_form"):
        preferred_name = st.text_input(
            "Preferred first name *",
            placeholder="e.g., Tessa",
            help=(
                "The interviewer will use this name during the practice session. "
                "It is cleared when you end the session or sign out."
            ),
        )
        st.caption("Enter a first name or nickname only—not your full legal name.")

        role_col, company_col = st.columns(2, gap="large")
        with role_col:
            job_title = st.text_input(
                "Job title *",
                placeholder="e.g., Data Analyst Intern",
            )
        with company_col:
            company = st.text_input(
                "Company or organization (optional)",
                placeholder="Type the employer name here",
            )

        st.markdown('<div class="setup-section">Application materials</div>', unsafe_allow_html=True)
        resume_col, description_col = st.columns(2, gap="large")
        with resume_col:
            resume = st.file_uploader(
                "Résumé *",
                type=["pdf", "docx"],
                help="Upload the résumé submitted or planned for this position.",
            )
            st.caption("Accepted formats: PDF or DOCX")
        with description_col:
            job_description_file = st.file_uploader(
                "Job description file (option 1)",
                type=["pdf", "docx", "txt"],
                help="Upload the complete job posting, or paste it below.",
            )
            job_description_text = st.text_area(
                "Paste the job description (option 2)",
                height=145,
                placeholder="Click here and paste the responsibilities, qualifications, and preferred skills...",
                help="Required if you do not upload a job-description file.",
            )
            st.caption("Upload a file above, or paste the complete posting in this box.")

        st.markdown('<div class="setup-section">Interview settings</div>', unsafe_allow_html=True)
        round_col, level_col, duration_col = st.columns(3, gap="large")
        with round_col:
            interview_round = st.selectbox(
                "Interview round",
                options=[
                    "Recruiter / HR screen",
                    "Hiring manager",
                    "Technical specialist",
                    "Panel / final interview",
                    "Full interview loop",
                ],
                index=2,
            )
        with level_col:
            challenge_level = st.selectbox(
                "Challenge level",
                options=["Supportive", "Realistic", "Challenging"],
                index=1,
            )
        with duration_col:
            interview_minutes = st.selectbox(
                "Interview length",
                options=[5, 10],
                index=1,
                format_func=lambda minutes: f"{minutes} minutes",
                help=(
                    "Practice sessions are currently limited to 10 minutes while "
                    "the app uses the shared free API allocation."
                ),
            )

        consent = st.checkbox(
            "I understand that my documents are used only for this practice session "
            "and will be cleared when I end the session or sign out."
        )
        st.caption(
            "A phone number or mailing address on a normal resume is acceptable. "
            "Please do not upload Social Security numbers, financial information, "
            "passwords, or other highly sensitive records."
        )
        submitted = st.form_submit_button(
            "Review interview profile",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        errors: list[str] = []
        if not preferred_name.strip():
            errors.append("Enter the preferred first name the interviewer should use.")
        if not job_title.strip():
            errors.append("Enter the job title.")
        if resume is None:
            errors.append("Upload your résumé.")
        if not job_description_text.strip() and job_description_file is None:
            errors.append("Paste or upload the job description.")
        if not consent:
            errors.append("Confirm the document privacy reminder.")

        if errors:
            for error in errors:
                st.error(error)
            return

        st.session_state.interview_setup = {
            "preferred_name": preferred_name.strip(),
            "job_title": job_title.strip(),
            "company": company.strip(),
            "resume_name": resume.name,
            "resume_bytes": resume.getvalue(),
            "job_description_text": job_description_text.strip(),
            "job_description_file_name": (
                job_description_file.name if job_description_file else None
            ),
            "job_description_file_bytes": (
                job_description_file.getvalue() if job_description_file else None
            ),
            "interview_round": interview_round,
            "challenge_level": challenge_level,
            "interview_minutes": interview_minutes,
        }
        st.session_state.pop("interview_profile", None)
        st.session_state.pop("student_background_answers", None)
        st.session_state.pop("interview_plan", None)
        st.session_state.pop("interview_transcript", None)
        st.session_state.pop("interview_feedback", None)
        st.session_state.app_screen = "profile_review"
        st.rerun()


def profile_review_page() -> None:
    """Analyze and review the evidence-grounded candidate/job profile."""
    setup = st.session_state.get("interview_setup", {})
    if not setup:
        st.session_state.app_screen = "setup"
        st.rerun()

    st.markdown("## Review your interview context")
    st.write(
        "Review the application context, then generate a profile grounded in the "
        "résumé and job description. The profile will guide the interview—not judge "
        "the student or make a hiring decision."
    )
    with st.container(border=True):
        st.markdown(f"**Preferred first name:** {setup['preferred_name']}")
        st.markdown(f"**Job title:** {setup['job_title']}")
        st.markdown(f"**Company:** {setup['company'] or 'Not provided'}")
        st.markdown(f"**Résumé:** {setup['resume_name']}")
        st.markdown(f"**Interview round:** {setup['interview_round']}")
        st.markdown(f"**Challenge level:** {setup['challenge_level']}")
        st.markdown(
            f"**Interview length:** {min(int(setup.get('interview_minutes', 10)), 10)} minutes"
        )

    profile = st.session_state.get("interview_profile")
    if profile:
        st.success("Profile generated. Please review it before continuing.")
        if profile.get("_model_used"):
            st.caption(f"Analysis model: {profile['_model_used']}")
        st.markdown(f"### {profile['candidate_summary']}")
        sections = [
            ("Education and academic focus", "education_and_focus"),
            ("Relevant experience", "relevant_experience"),
            ("Demonstrated skills", "demonstrated_skills"),
            ("What the role emphasizes", "role_priorities"),
            ("Strong matches", "strong_matches"),
            ("Topics to verify", "topics_to_verify"),
            ("Recommended interview focus", "interview_focus"),
        ]
        for title, key in sections:
            with st.expander(title, expanded=key in {"strong_matches", "interview_focus"}):
                items = profile.get(key, [])
                if items:
                    st.markdown("\n".join(f"- {item}" for item in items))
                else:
                    st.caption("Nothing identified from the supplied documents.")

        questions = profile.get("clarifying_questions", [])
        st.markdown("### Add useful background")
        if questions:
            st.write(
                "The documents do not answer a few job-relevant questions. These "
                "answers are optional and will be kept separate from résumé evidence."
            )
            existing_answers = st.session_state.get("student_background_answers", {})
            with st.form("student_background_form"):
                new_answers: dict[str, str] = {}
                for index, question in enumerate(questions):
                    new_answers[question] = st.text_area(
                        question,
                        value=existing_answers.get(question, ""),
                        key=f"background_answer_{index}",
                        placeholder="Optional—briefly describe your experience.",
                        height=100,
                    )
                if st.form_submit_button(
                    "Save background additions", use_container_width=True
                ):
                    st.session_state.student_background_answers = {
                        question: answer.strip()
                        for question, answer in new_answers.items()
                        if answer.strip()
                    }
                    st.success("Background additions saved for this practice session.")
        else:
            st.info(
                "The résumé and job description provide enough context to plan the interview."
            )

        if st.button(
            "Build interview plan",
            type="primary",
            use_container_width=True,
        ):
            api_key = google_api_key()
            if not api_key:
                st.error(
                    "A free Google AI Studio API key is required. Set GOOGLE_API_KEY "
                    "in the environment, then restart the app."
                )
            else:
                try:
                    with st.spinner("Designing a realistic interview sequence..."):
                        st.session_state.interview_plan = generate_interview_plan(
                            api_key=api_key,
                            job_title=setup["job_title"],
                            company=setup["company"],
                            interview_round=setup["interview_round"],
                            challenge_level=setup["challenge_level"],
                            interview_minutes=min(
                                int(setup.get("interview_minutes", 10)), 10
                            ),
                            profile=profile,
                            student_context=st.session_state.get(
                                "student_background_answers", {}
                            ),
                        )
                    st.session_state.app_screen = "plan_ready"
                    st.rerun()
                except ProfileAnalysisUnavailable as exc:
                    st.warning(str(exc))
                except Exception as exc:
                    st.error(f"Interview planning failed: {exc}")

    back_col, next_col = st.columns(2)
    with back_col:
        if st.button("Back to setup", use_container_width=True):
            st.session_state.app_screen = "setup"
            st.rerun()
    with next_col:
        analyze_label = "Regenerate profile" if profile else "Analyze résumé and job description"
        if st.button(analyze_label, type="primary", use_container_width=True):
            api_key = google_api_key()
            if not api_key:
                st.error(
                    "A free Google AI Studio API key is required. Set GOOGLE_API_KEY "
                    "in the environment, then restart the app."
                )
            else:
                try:
                    with st.spinner("Reading the documents and building the profile..."):
                        resume_text = redact_contact_details(
                            extract_document_text(
                                setup["resume_name"], setup["resume_bytes"]
                            )
                        )
                        description_parts = [setup["job_description_text"]]
                        if setup.get("job_description_file_bytes"):
                            description_parts.append(
                                redact_contact_details(extract_document_text(
                                    setup["job_description_file_name"],
                                    setup["job_description_file_bytes"],
                                ))
                            )
                        job_description = "\n\n".join(
                            part for part in description_parts if part
                        )
                        st.session_state.interview_profile = analyze_interview_profile(
                            api_key=api_key,
                            job_title=setup["job_title"],
                            company=setup["company"],
                            interview_round=setup["interview_round"],
                            challenge_level=setup["challenge_level"],
                            resume_text=resume_text,
                            job_description=job_description,
                        )
                        st.session_state.student_background_answers = {}
                        st.session_state.pop("interview_plan", None)
                    st.rerun()
                except DocumentParseError as exc:
                    st.error(str(exc))
                except ProfileAnalysisUnavailable as exc:
                    st.warning(str(exc))
                except Exception as exc:
                    st.error(f"Profile analysis failed: {exc}")

    st.divider()
    if st.button("End practice and clear uploaded data", use_container_width=True):
        clear_practice_data()
        st.success("Your uploaded documents and practice data have been cleared.")


def plan_ready_page() -> None:
    """Show a student-safe overview without revealing planned questions."""
    setup = st.session_state.get("interview_setup", {})
    plan = st.session_state.get("interview_plan", {})
    if not setup or not plan:
        st.session_state.app_screen = "profile_review"
        st.rerun()

    st.markdown("## Your interview is ready")
    st.write(
        f"The practice session has been tailored for **{setup['preferred_name']}** "
        f"and the **{setup['job_title']}** position. Questions remain hidden so the "
        "practice feels like a real interview."
    )
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Questions", len(plan.get("questions", [])))
    metric_col2.metric(
        "Interview length",
        f"{min(int(setup.get('interview_minutes', 10)), 10)} min",
    )
    metric_col3.metric("Round", setup["interview_round"])

    with st.container(border=True):
        st.markdown("### Areas the interview will cover")
        competencies = plan.get("competencies", [])
        st.markdown("\n".join(f"- {item}" for item in competencies))
        st.caption(
            f"Challenge level: {setup['challenge_level']} · "
            f"Planning model: {plan.get('_model_used', 'Gemini Flash')}"
        )

    st.info(
        "The interviewer may ask a follow-up when an answer needs clarification "
        "or when there is an opportunity to explore a strong answer more deeply."
    )
    back_col, start_col = st.columns(2)
    with back_col:
        if st.button("Back to profile", use_container_width=True):
            st.session_state.pop("live_token", None)
            st.session_state.app_screen = "profile_review"
            st.rerun()
    with start_col:
        if st.button("Start voice interview", type="primary", use_container_width=True):
            st.session_state.pop("live_token", None)
            st.session_state.pop("interview_transcript", None)
            st.session_state.pop("interview_feedback", None)
            st.session_state.app_screen = "voice_interview"
            st.rerun()

    st.divider()
    if st.button("End practice and clear uploaded data", use_container_width=True):
        clear_practice_data()
        st.success("Your uploaded documents and practice data have been cleared.")


def voice_interview_page() -> None:
    """Prepare a short-lived browser connection and conduct the voice interview."""
    setup = st.session_state.get("interview_setup", {})
    plan = st.session_state.get("interview_plan", {})
    if not setup or not plan:
        st.session_state.app_screen = "plan_ready"
        st.rerun()

    st.markdown(f"## {setup['job_title']} voice interview")
    st.caption(
        f"{setup['interview_round']} · {setup['challenge_level']} · "
        "Speak in English as you would in a real interview."
    )
    st.info(
        "Your browser will ask for microphone permission. The interviewer will ask "
        "one question at a time, beginning with a brief self-introduction. Detailed "
        "feedback is reserved until the interview ends."
    )

    token_info = st.session_state.get("live_token")
    if not token_info:
        st.markdown("### Get ready for your voice interview")
        st.write(
            "A secure, temporary connection will be created for this practice. "
            "Your session data will be cleared when you end the practice."
        )
        if st.button("Prepare voice interview", type="primary", use_container_width=True):
            api_key = google_api_key()
            if not api_key:
                st.error("GOOGLE_API_KEY is not configured for this app.")
                return
            instructions = build_live_instructions(
                preferred_name=setup["preferred_name"],
                job_title=setup["job_title"],
                interview_round=setup["interview_round"],
                plan=plan,
            )
            try:
                with st.spinner("Preparing the secure voice room..."):
                    st.session_state.live_token = mint_live_token(
                        api_key=api_key,
                        instructions=instructions,
                        interview_round=setup["interview_round"],
                    )
                st.rerun()
            except Exception as exc:
                message = str(exc)
                if "429" in message or "RESOURCE_EXHAUSTED" in message:
                    st.error(
                        "Gemini's current request limit has been reached. Wait for the "
                        "quota to reset, or use a billed API project, then try again."
                    )
                else:
                    st.error(f"The voice session could not be prepared: {message}")
    else:
        st.warning(
            "This one-use connection must be started within about one minute. "
            "Select Start voice interview below and allow microphone access."
        )
        result = live_interview_component(
            token=token_info["token"],
            model=token_info["model"],
            voice=token_info.get("voice", "Charon"),
            interview_round=setup["interview_round"],
            duration_minutes=min(int(setup.get("interview_minutes", 10)), 10),
            key=f"live_interview_{token_info['token'][-12:]}",
        )
        if result and result.get("status") == "completed":
            st.session_state.interview_transcript = result.get("transcript", [])
            st.session_state.interview_end_reason = result.get("reason", "student_ended")
            st.session_state.pop("live_token", None)
            st.session_state.app_screen = "feedback"
            st.rerun()
        if st.button("Create a fresh voice session", use_container_width=True):
            st.session_state.pop("live_token", None)
            st.rerun()

    back_col, end_col = st.columns(2)
    with back_col:
        if st.button("Back to interview plan", use_container_width=True):
            st.session_state.pop("live_token", None)
            st.session_state.app_screen = "plan_ready"
            st.rerun()
    with end_col:
        if st.button("End practice and clear uploaded data", use_container_width=True):
            clear_practice_data()
            st.rerun()


def feedback_page() -> None:
    """Show the captured transcript and generate student-facing coaching."""
    setup = st.session_state.get("interview_setup", {})
    profile = st.session_state.get("interview_profile", {})
    transcript = st.session_state.get("interview_transcript", [])
    if not setup or not transcript:
        st.session_state.app_screen = "plan_ready"
        st.rerun()

    st.markdown("## Interview feedback")
    if st.session_state.get("interview_end_reason") == "time_limit":
        st.info("The practice ended when the selected time limit was reached.")
    else:
        st.success("The voice interview ended and its transcript was saved for this session.")

    with st.expander("Review transcript", expanded=False):
        for turn in transcript:
            label = "You" if turn.get("role") == "candidate" else "Interviewer"
            st.markdown(f"**{label}:** {turn.get('text', '')}")
        st.caption(
            "Automatic speech transcription can contain errors. Feedback should be "
            "interpreted with those limitations in mind."
        )

    feedback = st.session_state.get("interview_feedback")
    if not feedback:
        st.write(
            "Generate a coaching summary based on what was captured in the transcript. "
            "This uses one additional Gemini request."
        )
        if st.button("Generate feedback", type="primary", use_container_width=True):
            try:
                with st.spinner("Reviewing the interview responses..."):
                    st.session_state.interview_feedback = generate_feedback(
                        api_key=google_api_key(),
                        setup=setup,
                        profile=profile,
                        transcript=transcript,
                    )
                st.rerun()
            except ProfileAnalysisUnavailable as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error(f"Feedback could not be generated: {exc}")
    else:
        st.markdown("### Overall coaching summary")
        st.write(feedback["summary"])
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("### What worked well")
            for item in feedback["strengths"]:
                with st.container(border=True):
                    st.markdown(f"**{item['observation']}**")
                    st.caption(f"Evidence: {item['evidence']}")
        with right:
            st.markdown("### What to improve")
            for item in feedback["improvements"]:
                with st.container(border=True):
                    st.markdown(f"**{item['observation']}**")
                    st.caption(f"Evidence: {item['evidence']}")
                    st.write(f"Next step: {item['next_step']}")
        st.markdown("### Communication")
        st.write(feedback["communication"])
        st.markdown("### Connection to the role")
        st.write(feedback["role_alignment"])
        st.markdown("### Focus for the next practice")
        for item in feedback["next_practice_focus"]:
            st.markdown(f"- {item}")
        st.caption(f"Feedback model: {feedback.get('_model_used', 'Gemini Flash')}")

        st.markdown("### Download your report")
        include_transcript = st.checkbox(
            "Include the full transcript as an appendix",
            value=False,
            help="The transcript may contain automatic speech-recognition errors.",
        )
        pdf_bytes = create_feedback_pdf(
            setup=setup,
            feedback=feedback,
            transcript=transcript,
            include_transcript=include_transcript,
        )
        st.download_button(
            "Download PDF report",
            data=pdf_bytes,
            file_name="flyer_interview_coaching_report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    st.divider()
    if st.button("End practice and clear all session data", use_container_width=True):
        clear_practice_data()
        st.rerun()


def text_interview_page() -> None:
    """Conduct the planned interview one question at a time."""
    setup = st.session_state.get("interview_setup", {})
    plan = st.session_state.get("interview_plan", {})
    runtime = st.session_state.get("interview_runtime", {})
    messages = st.session_state.get("interview_messages", [])
    if not setup or not plan or not runtime or not messages:
        st.session_state.app_screen = "plan_ready"
        st.rerun()

    total = len(plan["questions"])
    st.markdown(f"## {setup['job_title']} mock interview")
    st.caption(
        f"{setup['interview_round']} · {setup['challenge_level']} · "
        "Detailed feedback is saved until the interview ends."
    )
    completed_count = runtime["question_index"] + int(runtime["completed"])
    st.progress(
        min(completed_count / total, 1.0),
        text=f"Question {min(runtime['question_index'] + 1, total)} of {total}",
    )

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if runtime["completed"]:
        st.success("Interview complete. Your responses are ready for a feedback report.")
        st.button(
            "Generate feedback report",
            type="primary",
            disabled=True,
            help="The feedback report is the next development step.",
            use_container_width=True,
        )
        return

    answer = st.chat_input("Type your answer, then press Enter")
    if not answer:
        return

    question = plan["questions"][runtime["question_index"]]
    candidate_answers = [*runtime["current_answers"], answer.strip()]
    try:
        with st.spinner("The interviewer is considering your answer..."):
            turn = evaluate_answer(
                api_key=google_api_key(),
                question=question,
                answers=candidate_answers,
                follow_up_allowed=not runtime["follow_up_used"],
            )
    except Exception as exc:
        st.error(f"The interviewer could not process this answer: {exc}")
        st.caption("Your answer was not added. Copy it below before trying again:")
        st.code(answer)
        return

    messages.append({"role": "user", "content": answer.strip()})
    runtime["current_answers"] = candidate_answers
    runtime["assessments"].append({
        "question_index": runtime["question_index"],
        "assessment": turn["assessment"],
        "model": turn.get("_model_used"),
    })

    if turn["decision"] == "follow_up" and turn["follow_up_question"].strip():
        runtime["follow_up_used"] = True
        assistant_text = f"{turn['transition']}\n\n{turn['follow_up_question']}"
    else:
        runtime["question_index"] += 1
        runtime["follow_up_used"] = False
        runtime["current_answers"] = []
        if runtime["question_index"] >= total:
            runtime["completed"] = True
            assistant_text = f"{turn['transition']}\n\n{plan['closing_message']}"
        else:
            next_question = plan["questions"][runtime["question_index"]]["question"]
            assistant_text = f"{turn['transition']}\n\n{next_question}"

    messages.append({"role": "assistant", "content": assistant_text})
    st.session_state.interview_runtime = runtime
    st.session_state.interview_messages = messages
    st.rerun()


def app_page() -> None:
    """Render the authenticated or local-development application."""
    if dev_mode_enabled():
        st.caption("Local development mode · Authentication bypassed")
    else:
        user_name = st.user.get("name", st.user.get("email", "Flyer"))
        top_col, logout_col = st.columns([5, 1])
        top_col.caption(f"Signed in as {user_name}")
        logout_col.button("Sign out", on_click=logout_and_clear, use_container_width=True)

    screen = st.session_state.setdefault("app_screen", "setup")
    if screen == "profile_review":
        profile_review_page()
    elif screen == "plan_ready":
        plan_ready_page()
    elif screen == "voice_interview":
        voice_interview_page()
    elif screen == "feedback":
        feedback_page()
    elif screen == "text_interview":
        text_interview_page()
    else:
        setup_page()


if dev_mode_enabled():
    app_page()
elif getattr(st.user, "is_logged_in", False):
    if user_is_allowed():
        app_page()
    else:
        st.error("This application is available only to University of Dayton accounts.")
        st.button("Sign out", on_click=st.logout)
else:
    login_page()
