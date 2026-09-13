# RoleReady Interview Lab

RoleReady Interview Lab is a standalone Streamlit application for people to
practice job interviews tailored to a résumé, job description, job title, and
interview round.

## Project status

**Beta — ready for a small, supervised pilot.** The end-to-end workflow
is implemented and deployed. The beta is intended for usability, reliability,
and coaching-quality evaluation; it is not a hiring assessment or production
career-services platform. See [BETA_OVERVIEW.md](BETA_OVERVIEW.md) for the full
feature inventory, design boundaries, known limitations, and pilot checklist.

This is an independently implemented application. ChatISA was reviewed as an
early functional reference, but its source code is not incorporated into this
project.

## Beta workflow

1. Sign in with a Google account authorized for the closed beta.
2. Provide a job title, résumé, and job description.
3. Review the evidence-grounded candidate and role profile and optionally add
   missing job-relevant context.
4. Build a private interview plan adapted to the role, round, candidate
   background, challenge level, and selected duration.
5. Practice aloud with a voice-based virtual interviewer.
6. Review evidence-based coaching and preparation priorities, then optionally
   download a PDF report with or without the transcript.

## Run locally

From the repository root:

```powershell
conda activate interview
$env:ROLEREADY_DEV_MODE="true"
$env:GOOGLE_API_KEY="your-free-google-ai-studio-key"
python -m streamlit run app.py
```

Create a free-tier API key in Google AI Studio. Do not commit the key to Git or
place it directly in Python source code. The text and live models can be changed
without code edits by setting `ROLEREADY_TEXT_MODEL` and
`ROLEREADY_LIVE_MODEL`.

For local development, copy `.env.example` to `.env` inside this directory and
put the key there. The repository `.gitignore` excludes `.env` files.

## Privacy behavior

Uploaded documents are parsed in memory and are not written to the application
database or project folder. Practice data is cleared explicitly when the user
ends the practice session or signs out. Free-tier model providers may process
submitted content under their own data-use terms, so the interface warns users
not to upload highly sensitive records.

## Directory structure

```text
roleready_interview_lab/
├── app.py               # Streamlit entry point
├── assets/              # Avatar and interface assets
├── prompts/             # Interview-stage and feedback prompts
├── services/            # Authentication, model, audio, and PDF services
├── tests/               # Automated tests
└── README.md
```
