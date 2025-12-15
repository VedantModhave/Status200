from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

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
    # Replace emoji bullets with plain labels
    clean = clean.replace("🔍 ", "")
    clean = clean.replace("💡 ", "")
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
    story.append(Spacer(1, 12))


