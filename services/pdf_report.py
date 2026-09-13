"""Create an in-memory PDF coaching report for one practice session."""

from __future__ import annotations

from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

UD_RED = colors.HexColor("#CE1141")
UD_NAVY = colors.HexColor("#002F56")
UD_BLUE = colors.HexColor("#004B87")
LIGHT_BLUE = colors.HexColor("#EAF2F8")
LIGHT_GRAY = colors.HexColor("#F4F6F8")
TEXT = colors.HexColor("#172033")


def _text(value: object) -> str:
    return escape(str(value or "")).replace("\n", "<br/>")


def _page(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(UD_RED)
    canvas.setLineWidth(2)
    canvas.line(0.65 * inch, height - 0.45 * inch, width - 0.65 * inch, height - 0.45 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#596273"))
    canvas.drawString(0.65 * inch, 0.42 * inch, "RoleReady Interview Lab")
    canvas.drawRightString(width - 0.65 * inch, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


def create_feedback_pdf(
    *, setup: dict, feedback: dict, transcript: list[dict], include_transcript: bool
) -> bytes:
    """Return a polished PDF as bytes; no session content is written to disk."""
    stream = BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.7 * inch,
        title="RoleReady Interview Lab Coaching Report",
        author="RoleReady Interview Lab",
    )
    base = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold",
                           fontSize=23, leading=27, textColor=UD_NAVY, spaceAfter=8)
    subtitle = ParagraphStyle("Subtitle", parent=base["Normal"], fontSize=10,
                              leading=14, textColor=colors.HexColor("#596273"), spaceAfter=16)
    heading = ParagraphStyle("Heading", parent=base["Heading2"], fontName="Helvetica-Bold",
                             fontSize=14, leading=17, textColor=UD_NAVY,
                             spaceBefore=13, spaceAfter=7)
    body = ParagraphStyle("Body", parent=base["BodyText"], fontSize=10, leading=15,
                          textColor=TEXT, spaceAfter=7)
    small = ParagraphStyle("Small", parent=body, fontSize=8.5, leading=12,
                           textColor=colors.HexColor("#596273"))
    tag = ParagraphStyle("Tag", parent=body, fontName="Helvetica-Bold", fontSize=9,
                         leading=12, textColor=UD_BLUE, spaceAfter=3)
    centered = ParagraphStyle("Centered", parent=small, alignment=TA_CENTER)

    story = [
        Spacer(1, 0.08 * inch),
        Paragraph("RoleReady Interview Lab", tag),
        Paragraph("Mock Interview Coaching Report", title),
        Paragraph(
            "A developmental practice summary - not a hiring recommendation or formal assessment.",
            subtitle,
        ),
    ]
    details = [
        [Paragraph("Candidate", tag), Paragraph(_text(setup.get("preferred_name", "Student")), body)],
        [Paragraph("Position", tag), Paragraph(_text(setup.get("job_title")), body)],
        [Paragraph("Organization", tag), Paragraph(_text(setup.get("company") or "Not provided"), body)],
        [Paragraph("Practice format", tag), Paragraph(
            _text(f"{setup.get('interview_round', '')} | {setup.get('challenge_level', '')} | "
                  f"{min(int(setup.get('interview_minutes', 10)), 10)} minutes"), body)],
    ]
    table = Table(details, colWidths=[1.25 * inch, 5.2 * inch], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D8E5")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Paragraph("Overall coaching summary", heading),
                  Paragraph(_text(feedback.get("summary")), body)])

    story.append(Paragraph("What worked well", heading))
    for item in feedback.get("strengths", []):
        story.append(KeepTogether([
            Paragraph("+ " + _text(item.get("observation")), tag),
            Paragraph("<b>Evidence:</b> " + _text(item.get("evidence")), body),
        ]))

    story.append(Paragraph("What to improve", heading))
    for item in feedback.get("improvements", []):
        box = Table([[Paragraph(
            "<b>" + _text(item.get("observation")) + "</b><br/>"
            "<font color='#596273'>Evidence: " + _text(item.get("evidence")) + "</font><br/>"
            "<b>Next step:</b> " + _text(item.get("next_step")), body)]], colWidths=[6.45 * inch])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                                 ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8DEE6")),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                                 ("TOPPADDING", (0, 0), (-1, -1), 8),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        story.extend([box, Spacer(1, 6)])

    story.extend([
        Paragraph("Communication", heading),
        Paragraph(_text(feedback.get("communication")), body),
        Paragraph("Connection to the role", heading),
        Paragraph(_text(feedback.get("role_alignment")), body),
    ])
    priorities = feedback.get("preparation_priorities", [])
    if priorities:
        story.extend([
            Paragraph("Preparation priorities", heading),
            Paragraph(
                "Potential bottlenecks are included only when supported by the supplied "
                "materials and responses. They are preparation advice, not judgments "
                "about ability, employability, or hiring outcomes.",
                small,
            ),
        ])
        for item in priorities:
            box = Table([[Paragraph(
                "<b>" + _text(item.get("priority")) + "</b><br/>"
                "<font color='#596273'>Evidence considered: "
                + _text(item.get("evidence_basis")) + "</font><br/>"
                "<b>Recommended action:</b> "
                + _text(item.get("recommendation")), body)]], colWidths=[6.45 * inch])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D8E5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.extend([box, Spacer(1, 6)])

    story.append(Paragraph("Focus for the next practice", heading))
    for item in feedback.get("next_practice_focus", []):
        story.append(Paragraph("- " + _text(item), body))
    story.extend([Spacer(1, 8), Paragraph(
        "AI-generated coaching may reflect transcription errors. Review the transcript and use "
        "this report as practice guidance rather than a definitive evaluation.", small)])

    if include_transcript:
        story.extend([PageBreak(), Paragraph("Transcript appendix", title),
                      Paragraph("Automatically generated and may contain transcription errors.", subtitle)])
        for turn in transcript:
            label = "Candidate" if turn.get("role") == "candidate" else "Interviewer"
            story.append(KeepTogether([
                Paragraph(_text(label), tag),
                Paragraph(_text(turn.get("text")), body),
            ]))
        story.append(Paragraph("End of transcript", centered))

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return stream.getvalue()
