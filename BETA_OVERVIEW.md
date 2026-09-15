# RoleReady Interview Lab — Beta Overview

Last consolidated: September 13, 2026

## Beta definition

RoleReady Interview Lab has a complete deployable beta workflow: an authorized user
can provide real application materials, review the interpreted context, complete
a time-limited spoken interview, receive coaching, and download a report.

The beta is ready for a small, supervised closed pilot. It
is not yet positioned as an institution-wide service, commercial product, hiring
screen, or predictor of employability.

## Current participant workflow

1. Sign in with a Google account authorized for the closed beta.
2. Enter a preferred first name and job title; employer name is optional.
3. Upload a résumé in PDF or DOCX format.
4. Upload a job description in PDF, DOCX, or TXT format, or paste its text.
5. Select the closest interview round, challenge level, and a 5- or 10-minute
   practice duration.
6. Review a profile grounded in the résumé and job description.
7. Optionally answer a small number of clarifying questions when important
   context is missing.
8. Build and review a candidate-safe overview of the private interview plan.
9. Complete the spoken mock interview.
10. Review the transcript and generate coaching feedback.
11. Download a PDF coaching report, optionally with the transcript appendix.
12. End the practice or sign out to clear session data.

## Implemented features

### Access and session safety

- Google OIDC sign-in.
- Google OAuth test-user access controls the current closed pilot.
- Clear signed-in identity and a secure sign-out control.
- Uploaded documents and practice state are held in the Streamlit session rather
  than deliberately written to the repository or an application database.
- Practice data is cleared when the user ends the session or signs out.
- Gemini Live connections use short-lived, single-use tokens; the API key remains
  server-side in Streamlit Secrets.
- Contact details are redacted from extracted document text before analysis where
  supported by the parser.
- Consent and sensitive-information reminders appear before processing.

### Evidence-grounded preparation

- Required résumé, job description, and job title prevent generic interviews.
- Profile analysis separates demonstrated evidence, strong matches, role
  priorities, and topics that still need verification.
- Missing information is treated as unknown rather than proof of a deficiency.
- Career stage is inferred only from résumé evidence, not from educational status,
  degree, major, or presumed age.
- Optional clarifying answers are kept conceptually separate from résumé evidence.
- A major or course title alone is not treated as proof of mastery.

### Context-aware interview planning

- Supported rounds:
  - Initial screening (recruiter or HR)
  - Direct supervisor or hiring lead
  - Subject-matter or skills interview
  - Panel or final interview
  - Full interview process
- Supportive, realistic, and challenging levels change depth without making the
  interviewer rude or adversarial.
- Planning adapts to work setting, role function, inferred seniority, assessment
  style, and a plausible simulated interviewer identity.
- Simulated interviewer roles represent a useful practice perspective, not a
  prediction of an employer's actual reporting structure or hiring process. When
  several roles are plausible, the app uses a broader, neutral title.
- A generic round can map appropriately to a principal, department chair, dean,
  or search committee for education roles.
- Teaching demonstrations, portfolios, and research talks are discussed through
  preparation, choices, and reflection when the system did not observe them.
- The private plan includes a self-presentation question, role-relevant
  competencies, follow-ups, and rubrics without revealing questions in advance.

### Spoken interview experience

- Real-time audio conversation through Gemini Live.
- Tone follows the selected round: warmer for an initial screen, focused for a
  hiring lead, precise for a subject-matter interview, and structured for a panel.
- Four interviewer personas are selected randomly without using candidate data.
- Each appearance remains paired with its voice, while role, tone, and question
  depth are controlled independently by the interview context.
- The interviewer asks adaptive follow-ups and closes when the plan or time limit
  is complete.
- Substantial non-English answers receive a neutral request to retry in English;
  accents are not criticized or treated as evidence of communication ability.
- Input and output transcripts are assembled for session feedback.

### Coaching and reports

- Overall coaching summary.
- Evidence-linked strengths and improvement areas.
- Communication and connection-to-role observations.
- Specific focus areas for the next practice.
- **Preparation priorities** identify potential career-readiness bottlenecks only
  when a central role requirement and supplied evidence support the observation.
- Priorities distinguish unclear evidence from an absent qualification, recommend
  an action, and do not judge ability, employability, fit, or hiring likelihood.
- The section is omitted when evidence is insufficient or no material bottleneck
  is apparent.
- Downloadable PDF report with an optional transcript appendix and explicit
  AI/transcription limitations.

### Interface and accessibility work

- Responsive Streamlit layout for common desktop and mobile widths.
- Explicit styling for readable controls under Light, Dark, and System themes.
- Consistent red and blue visual language.
- Maintainer identification and Responsible AI guidance on the sign-in page.

## Models and infrastructure

- Primary text model: `gemini-3.7-flash`
- Text fallbacks: `gemini-3.6-flash`, then `gemini-3.5-flash-lite`
- Live voice model: `gemini-3.1-flash-live-preview`
- Hosting: Streamlit Community Cloud
- Source deployment: private GitHub repository, `main` branch
- Production configuration: Streamlit Secrets; local configuration: ignored
  `.env` file

Text models perform profile analysis, interview planning, and post-interview
feedback. Gemini Live handles the spoken interview. Model choice is an
administrator setting and is intentionally not exposed to participants.

## Deliberate product boundaries

The beta prepares participants to do the work themselves. It does not:

- write, rewrite, or submit a résumé or cover letter;
- invent skills, achievements, metrics, projects, or experience;
- equate coursework with demonstrated professional competence;
- score or rank candidates, recommend hiring, or predict employment outcomes;
- infer protected traits or select an interviewer from candidate characteristics;
- evaluate appearance, body language, accent, or personality;
- expose a long occupational taxonomy or participant-facing model selector;
- retain a permanent application library, history, or transcript archive.

A possible résumé coach is deferred as a separate future application. Its
governing principle would be to improve evidence and clarity—not the appearance
of experience.

## Known beta limitations

- The current Google OAuth project is in testing mode, so pilot users must be
  added individually as test users. A broader release requires an appropriate
  Google OAuth publishing configuration.
- The shared API allocation can be exhausted, and provider availability can
  temporarily prevent analysis, planning, voice, or feedback.
- The live model is a preview model and may change or be withdrawn.
- Voice sessions are capped at 10 minutes.
- Automatic transcription can omit or misrecognize speech; feedback is limited by
  the transcript it receives.
- AI-generated profiles, questions, and feedback can be incomplete or wrong.
- Current voices speak highly fluent English; accent variation is deferred.
- The four current avatar images are provisional pending original artwork.
- Uploaded content is sent to the configured model provider even though the app
  does not intentionally persist it.
- Automated test coverage remains limited.

## Pilot evaluation checklist

### Completion and reliability

- Can each test user sign in and sign out without administrative privileges?
- Can supported document formats be parsed reliably?
- Can users finish the complete workflow without assistance?
- Does microphone permission and live audio work on their devices?
- Does data clear after completion, manual exit, timeout, and sign-out?
- Are quota and provider failures explained clearly?

### Interview quality

- Are questions traceable to the résumé, role, or supplied context?
- Does inferred seniority match evidence rather than educational status?
- Does the interviewer identity fit the role and round?
- Are tone, difficulty, follow-ups, and duration realistic?
- Does random persona selection remain independent of candidate traits?

### Feedback quality and fairness

- Does every important observation cite recognizable evidence?
- Are transcription uncertainties handled cautiously?
- Are Preparation priorities sparse and supported by meaningful evidence?
- Are recommendations practical without becoming résumé writing or judgments?
- Can participants explain and act on the feedback?

### Usability and accessibility

- Are instructions and interview-round choices understandable without coaching?
- Are controls readable in Light, Dark, and System modes?
- Is the layout usable on common laptop and phone sizes?
- Do participants understand what is processed, cleared, and not formally evaluated?

## Post-pilot priorities

1. Fix blockers and recurring confusion found in pilot testing.
2. Evaluate grounding, feedback usefulness, and false-positive skill-gap
   observations using de-identified test cases.
3. Expand automated tests for parsers, schemas, session clearing, PDF reports, and
   deployment configuration.
4. Decide on OAuth publication after the closed pilot is satisfactory.
5. Add usage and cost controls before a broader rollout or paid-model change.
6. Replace provisional avatars after original artwork passes the documented asset
   and licensing requirements.

Commercialization, multilingual practice, accent variation, longer sessions, and
a separate résumé coach remain future possibilities, not beta commitments.
