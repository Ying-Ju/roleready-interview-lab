# Flyer Interview Lab

Flyer Interview Lab is a standalone Streamlit application for University of
Dayton students to practice job interviews tailored to a résumé, job
description, job title, and interview round.

## Project status

This is an independently implemented application. ChatISA was reviewed as an
early functional reference, but its source code is not incorporated into this
project.

## Planned workflow

1. Sign in with a University of Dayton account.
2. Provide a job title, résumé, and job description.
3. Confirm the student profile inferred from the résumé.
4. Select an interview round or a full interview loop.
5. Practice with a voice-based virtual interviewer.
6. Review feedback and download an interview report.

## Run locally

From the repository root:

```powershell
conda activate interview
$env:FLYER_DEV_MODE="true"
$env:GOOGLE_API_KEY="your-free-google-ai-studio-key"
python -m streamlit run flyer_interview_lab/app.py
```

Create a free-tier API key in Google AI Studio. Do not commit the key to Git or
place it directly in Python source code. The text model can be changed without
code edits by setting `FLYER_TEXT_MODEL`.

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
flyer_interview_lab/
├── app.py               # Streamlit entry point
├── assets/              # Avatar and interface assets
├── prompts/             # Interview-stage and feedback prompts
├── services/            # Authentication, model, audio, and PDF services
├── tests/               # Automated tests
└── README.md
```
