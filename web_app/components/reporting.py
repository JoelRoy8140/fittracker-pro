# web_app/components/reporting.py
"""
PDF export for workout plans and progress data.
Uses reportlab (must be installed: pip install reportlab).
"""

import io
from datetime import datetime
from typing import Dict, List, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# ─── colour palette ──────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor("#6C5CE7")
ACCENT    = colors.HexColor("#00B894")
TEXT_DARK = colors.HexColor("#2D3436")
BG_LIGHT  = colors.HexColor("#F8F9FA")


def _styles():
    base = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=base["h1"],
                         textColor=PRIMARY, fontSize=22, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=base["h2"],
                         textColor=PRIMARY, fontSize=14, spaceAfter=4)
    body = ParagraphStyle("Body", parent=base["Normal"],
                           textColor=TEXT_DARK, fontSize=10, leading=14)
    caption = ParagraphStyle("Caption", parent=base["Normal"],
                              textColor=colors.grey, fontSize=8, leading=10)
    return h1, h2, body, caption


# ─────────────────────────────────────────────────────────────────────────────
# Core export functions
# ─────────────────────────────────────────────────────────────────────────────

def generate_workout_pdf(user: Dict[str, Any], plan: Dict[str, Any]) -> bytes:
    """Return PDF bytes for a workout plan."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    h1, h2, body, caption = _styles()
    story = []

    # Header
    story.append(Paragraph("🏋️ FitTracker Pro – Workout Plan", h1))
    story.append(Paragraph(
        f"User: <b>{user.get('name','—')}</b>   |   "
        f"Goal: <b>{user.get('goal','—')}</b>   |   "
        f"Generated: {datetime.now().strftime('%d %b %Y')}",
        caption))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=12))

    split = plan.get("split", "Full Body")
    story.append(Paragraph(f"Split: {split}", h2))
    story.append(Spacer(1, 6))

    week = plan.get("week", {})
    if week:
        for day_name, day_data in week.items():
            story.append(Paragraph(day_name, h2))
            story.append(Paragraph(f"Focus: {day_data.get('focus','')}", caption))
            exercises = day_data.get("exercises", [])
            if exercises:
                table_data = [["Exercise", "Sets", "Reps", "Rest (s)"]]
                for ex in exercises:
                    table_data.append([
                        ex.get("name", "—"),
                        str(ex.get("sets", "—")),
                        str(ex.get("reps", "—")),
                        str(ex.get("rest", "—")),
                    ])
                tbl = Table(table_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
                tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                    ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE",   (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_LIGHT, colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("TOPPADDING",    (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(tbl)
            story.append(Spacer(1, 12))
    else:
        # flat list fallback
        exercises = plan.get("exercises", [])
        table_data = [["Exercise", "Sets", "Reps", "Rest"]]
        for ex in exercises:
            table_data.append([ex.get("name","—"), str(ex.get("sets","—")),
                               str(ex.get("reps","—")), str(ex.get("rest","—"))])
        if len(table_data) > 1:
            tbl = Table(table_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), PRIMARY),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(tbl)

    doc.build(story)
    return buf.getvalue()


def generate_progress_pdf(user: Dict[str, Any], measurements: List) -> bytes:
    """Return PDF bytes for a progress report."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    h1, h2, body, caption = _styles()
    story = []

    story.append(Paragraph("📈 FitTracker Pro – Progress Report", h1))
    story.append(Paragraph(
        f"User: <b>{user.get('name','—')}</b>   |   "
        f"Exported: {datetime.now().strftime('%d %b %Y')}",
        caption))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    if not measurements:
        story.append(Paragraph("No measurement data recorded yet.", body))
    else:
        table_data = [["Date", "Weight (kg)", "BMI", "Body Fat %"]]
        for row in measurements:
            table_data.append([
                str(row[2])[:10],  # date
                str(row[6]),       # weight
                str(row[3]),       # bmi
                str(row[4]),       # body fat
            ])
        tbl = Table(table_data, colWidths=[5*cm, 4*cm, 3*cm, 4*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_LIGHT, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)

    doc.build(story)
    return buf.getvalue()
