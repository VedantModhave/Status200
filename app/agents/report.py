import base64
from io import BytesIO
from pathlib import Path
from typing import List

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .state import ConversationState, AgentResult


REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"


def _clean_markdown(text: str) -> str:
    """
    Remove basic markdown and emoji markers for a cleaner PDF.
    """
    if not text:
        return ""

    # Strip bold markers
    clean = text.replace("**", "")
    # Normalise markdown list bullets to simple line breaks with dashes
    clean = clean.replace("\n- ", "<br/>- ")
    return clean


def generate_pdf_report(state: ConversationState) -> str:
    """
    Very simple PDF generator using reportlab.
    Returns the file path of the generated report.
    """
    REPORTS_DIR.mkdir(exist_ok=True)

    safe_molecule = state.molecule.replace(" ", "_")
    filename = f"report_{safe_molecule}.pdf"
    report_path = REPORTS_DIR / filename

    styles = getSampleStyleSheet()
    story: List = []

    title = f"EY Pharma Agentic AI – Innovation Brief for {state.molecule}"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    meta = (
        f"Region: {state.region} | Time Horizon: {state.time_horizon} | "
        f"User Query: {state.user_query}"
    )
    story.append(Paragraph(meta, styles["Normal"]))
    story.append(Spacer(1, 24))

    if state.final_summary:
        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        summary_text = _clean_markdown(state.final_summary)
        story.append(Paragraph(summary_text, styles["Normal"]))
        story.append(Spacer(1, 18))

    for key, result in state.agent_results.items():
        _append_agent_section(story, result, styles)

    doc = SimpleDocTemplate(str(report_path), pagesize=A4)
    doc.build(story)

    return str(report_path)


def _append_agent_section(story: list, result: AgentResult, styles) -> None:
    story.append(Paragraph(result.agent_name, styles["Heading3"]))
    story.append(Spacer(1, 6))
    # Clean markdown in agent summaries as well
    clean_summary = _clean_markdown(result.summary)
    story.append(Paragraph(clean_summary, styles["Normal"]))
    story.append(Spacer(1, 6))
    
    # Add charts
    if result.charts:
        for chart in result.charts:
            try:
                chart_data = base64.b64decode(chart.get('data', ''))
                img = Image(BytesIO(chart_data), width=6*inch, height=3.75*inch)
                story.append(img)
                story.append(Spacer(1, 6))
            except Exception:
                pass  # Skip if chart can't be loaded
    
    # Add tables
    if result.tables:
        for table_data in result.tables:
            rows = table_data.get('rows', [])
            if rows:
                df = pd.DataFrame(rows)
                # Convert DataFrame to list of lists for ReportLab
                table_rows = [df.columns.tolist()] + df.values.tolist()
                tbl = Table(table_rows)
                tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(tbl)
                story.append(Spacer(1, 12))
    
    story.append(Spacer(1, 6))


