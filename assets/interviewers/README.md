# Interviewer avatar replacement guide

These four images are provisional, fictional AI-generated development assets. The
app randomly selects one persona for each new practice and keeps that person's voice
and appearance together. Interview role, tone, and question depth are controlled
separately. Selection never uses candidate data, and students do not select the
interviewer.

## Required files

- `production/recruiter.png` — Persona 1 (legacy filename)
- `production/hiring_manager.png` — Persona 2 (legacy filename)
- `production/technical_interviewer.png` — Persona 3 (legacy filename)
- `production/panel_chair.png` — Persona 4 (legacy filename)

To replace the artwork without changing the code, keep the filenames above.

## Drawing specification

- Square PNG, ideally 1024 × 1024 pixels or larger
- Transparent background (real alpha transparency, not a checkerboard drawn into the image)
- Chest-up composition, subject centered, with similar head size and placement across all four files
- Professional but approachable expression
- Each character must be credible in any interviewer role; do not encode one as
  inherently HR, managerial, technical, or senior
- No university logo, employer logo, words, signature, or watermark
- Original artwork only; do not trace or closely imitate an identifiable real person or copyrighted character

The current interface creates subtle whole-character states for idle, thinking, listening, and speaking. A later facial-animation version can add separate eye and mouth layers after the final character drawings are available.
