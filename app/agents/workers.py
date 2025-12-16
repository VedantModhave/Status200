import json
import base64
from io import BytesIO
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from .state import ConversationState, AgentResult

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def iqvia_insights_agent(state: ConversationState) -> ConversationState:
    # Check if this agent should run
    if not any(task.get("agent") == "iqvia" for task in state.tasks):
        return state
    
    csv_path = DATA_DIR / "iqvia_markets.csv"
    df = pd.read_csv(csv_path)
    df_filt = df[(df["molecule"] == state.molecule) & (df["country"] == state.region)]

    if df_filt.empty:
        # Check if molecule exists in other regions or region exists for other molecules
        molecule_exists = (df["molecule"] == state.molecule).any()
        region_exists = (df["country"] == state.region).any()
        
        if molecule_exists and not region_exists:
            available_regions = df[df["molecule"] == state.molecule]["country"].unique().tolist()
            summary = (
                f"**Data Not Available for {state.region}**\n\n"
                f"No IQVIA mock data found for {state.molecule} in {state.region}. "
                f"However, data is available for this molecule in: {', '.join(available_regions)}. "
                f"In a production system, this would query real-time market data or fall back to broader geographies."
            )
        elif region_exists and not molecule_exists:
            available_molecules = df[df["country"] == state.region]["molecule"].unique().tolist()[:5]
            summary = (
                f"**Molecule Not in Dataset**\n\n"
                f"No IQVIA mock data found for {state.molecule} in {state.region}. "
                f"Available molecules in {state.region} include: {', '.join(available_molecules)}. "
                f"In a production system, this would query real-time market databases."
            )
        else:
            summary = (
                f"**Data Not Available**\n\n"
                f"No IQVIA mock data found for {state.molecule} in {state.region}. "
                f"This is a demo system with limited mock data. In production, this would query "
                f"real-time IQVIA databases or similar market intelligence sources."
            )
        tables = []
        charts = []
    else:
        base_year = df_filt["year"].min()
        latest_year = df_filt["year"].max()
        base_size = float(df_filt.loc[df_filt["year"] == base_year, "market_size_usd_mn"].iloc[0])
        latest_size = float(df_filt.loc[df_filt["year"] == latest_year, "market_size_usd_mn"].iloc[0])
        cagr = float(df_filt["cagr_pct"].iloc[-1])

        summary = (
            f"Market for {state.molecule} in {state.region} grew from "
            f"USD {base_size:.0f}m in {base_year} to {latest_size:.0f}m in {latest_year}, "
            f"with a CAGR of ~{cagr:.1f}%. Competition is moderate with "
            f"{int(df_filt['competitors'].iloc[-1])} active players."
        )

        tables = [
            {
                "name": "iqvia_markets",
                "rows": df_filt.to_dict(orient="records"),
            }
        ]
        
        # Generate market trend chart
        fig, ax = plt.subplots(figsize=(8, 5))
        df_sorted = df_filt.sort_values("year")
        ax.plot(df_sorted["year"], df_sorted["market_size_usd_mn"], marker="o", linewidth=2, markersize=8)
        ax.set_xlabel("Year")
        ax.set_ylabel("Market Size (USD Million)")
        ax.set_title(f"Market Growth Trend: {state.molecule} in {state.region}")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64 for embedding
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        chart_data = base64.b64encode(buf.read()).decode()
        plt.close()
        
        charts = [
            {
                "name": "market_trend",
                "type": "line",
                "data": chart_data,
                "title": f"Market Growth Trend: {state.molecule} in {state.region}",
            }
        ]

    state.agent_results["iqvia"] = AgentResult(
        agent_name="IQVIA Insights Agent",
        summary=summary,
        tables=tables,
        charts=charts,
    )
    return state


def exim_trade_agent(state: ConversationState) -> ConversationState:
    # Check if this agent should run
    if not any(task.get("agent") == "exim" for task in state.tasks):
        return state
    
    csv_path = DATA_DIR / "exim_trade.csv"
    df = pd.read_csv(csv_path)
    df_filt = df[(df["molecule"] == state.molecule) & (df["country"] == state.region)]

    if df_filt.empty:
        # Check for partial matches
        molecule_exists = (df["molecule"] == state.molecule).any()
        region_exists = (df["country"] == state.region).any()
        
        if molecule_exists and not region_exists:
            available_regions = df[df["molecule"] == state.molecule]["country"].unique().tolist()
            summary = (
                f"**EXIM Data Not Available for {state.region}**\n\n"
                f"No EXIM trade data found for {state.molecule} in {state.region}. "
                f"Data available in: {', '.join(available_regions)}. "
                f"In production, this would query real-time trade databases."
            )
        else:
            summary = (
                f"**EXIM Data Not Available**\n\n"
                f"No EXIM trade data found for {state.molecule} in {state.region}. "
                f"In a production system, this would query government trade databases or "
                f"commercial trade intelligence platforms."
            )
        tables = []
        charts = []
    else:
        latest = df_filt.sort_values("year").iloc[-1]
        summary = (
            f"In {state.region}, latest mock EXIM data shows imports of "
            f"{latest['import_volume_kg']} kg and exports of {latest['export_volume_kg']} kg "
            f"for {state.molecule}, at an average unit price of "
            f"USD {latest['unit_price_usd']:.0f}. Key source countries: "
            f"{latest['top_source_countries']}."
        )
        tables = [
            {
                "name": "exim_trade",
                "rows": df_filt.to_dict(orient="records"),
            }
        ]
        
        # Generate EXIM trade volume chart
        fig, ax = plt.subplots(figsize=(8, 5))
        df_sorted = df_filt.sort_values("year")
        ax.bar(df_sorted["year"] - 0.2, df_sorted["import_volume_kg"], width=0.4, label="Imports", alpha=0.8)
        ax.bar(df_sorted["year"] + 0.2, df_sorted["export_volume_kg"], width=0.4, label="Exports", alpha=0.8)
        ax.set_xlabel("Year")
        ax.set_ylabel("Volume (kg)")
        ax.set_title(f"EXIM Trade Volumes: {state.molecule} in {state.region}")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        chart_data = base64.b64encode(buf.read()).decode()
        plt.close()
        
        charts = [
            {
                "name": "exim_volumes",
                "type": "bar",
                "data": chart_data,
                "title": f"EXIM Trade Volumes: {state.molecule} in {state.region}",
            }
        ]

    state.agent_results["exim"] = AgentResult(
        agent_name="EXIM Trade Agent",
        summary=summary,
        tables=tables,
        charts=charts,
    )
    return state


def patent_landscape_agent(state: ConversationState) -> ConversationState:
    # Check if this agent should run
    if not any(task.get("agent") == "patent" for task in state.tasks):
        return state
    
    json_path = DATA_DIR / "patents.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    relevant = [p for p in data if p["molecule"] == state.molecule]

    if not relevant:
        # Check what molecules have patent data
        all_molecules = list(set(p.get("molecule") for p in data))
        summary = (
            f"**Patent Data Not Available**\n\n"
            f"No mock patent records found for {state.molecule}. "
            f"Available molecules in patent database: {', '.join(all_molecules[:5])}. "
            f"In production, this would query USPTO, WIPO, or other patent databases in real-time."
        )
        tables = []
    else:
        soon_expiring = sorted(relevant, key=lambda p: p["expiry_year"])
        next_expiry = soon_expiring[0]
        summary = (
            f"Mock patent landscape shows {len(relevant)} filings for {state.molecule}. "
            f"Earliest expiry is {next_expiry['patent_no']} ({next_expiry['patent_type']}) "
            f"expiring in {next_expiry['expiry_year']} with FTO risk rated "
            f"'{next_expiry['fto_risk']}'."
        )
        tables = [
            {
                "name": "patents",
                "rows": relevant,
            }
        ]

    state.agent_results["patent"] = AgentResult(
        agent_name="Patent Landscape Agent",
        summary=summary,
        tables=tables,
    )
    return state


def clinical_trials_agent(state: ConversationState) -> ConversationState:
    # Check if this agent should run
    if not any(task.get("agent") == "clinical_trials" for task in state.tasks):
        return state
    
    csv_path = DATA_DIR / "clinical_trials.csv"
    df = pd.read_csv(csv_path)
    df_filt = df[(df["molecule"] == state.molecule) & (df["country"] == state.region)]

    if df_filt.empty:
        # Check for partial matches
        molecule_exists = (df["molecule"] == state.molecule).any()
        region_exists = (df["country"] == state.region).any()
        
        if molecule_exists and not region_exists:
            available_regions = df[df["molecule"] == state.molecule]["country"].unique().tolist()
            summary = (
                f"**Trial Data Not Available for {state.region}**\n\n"
                f"No clinical trial records found for {state.molecule} in {state.region}. "
                f"Trials available in: {', '.join(available_regions)}. "
                f"In production, this would query ClinicalTrials.gov or WHO ICTRP databases."
            )
        else:
            summary = (
                f"**Trial Data Not Available**\n\n"
                f"No clinical trial records found for {state.molecule} in {state.region}. "
                f"In production, this would query ClinicalTrials.gov, WHO ICTRP, or other "
                f"clinical trial registries in real-time."
            )
        tables = []
        charts = []
    else:
        active = df_filt[df_filt["status"].isin(["Active", "Recruiting"])]
        phases = active["phase"].value_counts().to_dict()
        summary = (
            f"Mock clinical pipeline in {state.region} shows {len(active)} active or "
            f"recruiting trials for {state.molecule}, across phases: {phases}."
        )
        tables = [
            {
                "name": "clinical_trials",
                "rows": df_filt.to_dict(orient="records"),
            }
        ]
        
        # Generate phase distribution chart
        if len(active) > 0:
            phase_counts = active["phase"].value_counts()
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(phase_counts.index, phase_counts.values, alpha=0.8, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
            ax.set_xlabel("Trial Phase")
            ax.set_ylabel("Number of Trials")
            ax.set_title(f"Active Clinical Trials by Phase: {state.molecule} in {state.region}")
            ax.grid(True, alpha=0.3, axis="y")
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            chart_data = base64.b64encode(buf.read()).decode()
            plt.close()
            
            charts = [
                {
                    "name": "trial_phases",
                    "type": "bar",
                    "data": chart_data,
                    "title": f"Active Clinical Trials by Phase: {state.molecule}",
                }
            ]
        else:
            charts = []

    state.agent_results["clinical_trials"] = AgentResult(
        agent_name="Clinical Trials Agent",
        summary=summary,
        tables=tables,
        charts=charts,
    )
    return state


def internal_insights_agent(state: ConversationState) -> ConversationState:
    """
    Process internal documents if uploaded, otherwise return mock insights.
    Extracts text from PDFs and generates insights.
    """
    # Check if this agent should run
    if not any(task.get("agent") == "internal" for task in state.tasks):
        return state
    
    # Process uploaded PDF if available
    if state.uploaded_doc and PDF_AVAILABLE:
        try:
            pdf_file = BytesIO(state.uploaded_doc)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"Page {page_num + 1}:\n{text}")
            
            full_text = "\n\n".join(text_content)
            
            # Simple keyword-based analysis (in production, use LLM/RAG)
            keywords_found = []
            key_terms = [
                "adherence", "access", "market", "opportunity", "strategy", 
                "patient", "unmet need", "competition", "growth", "innovation"
            ]
            
            text_lower = full_text.lower()
            for term in key_terms:
                if term in text_lower:
                    keywords_found.append(term)
            
            # Generate summary based on extracted content
            if keywords_found:
                summary = (
                    f"**Document Analysis Complete**\n\n"
                    f"Extracted {len(pdf_reader.pages)} page(s) from uploaded document. "
                    f"Key themes identified: {', '.join(keywords_found[:5])}. "
                    f"Document highlights strategic considerations around {state.molecule} "
                    f"including market dynamics, patient access patterns, and potential "
                    f"innovation opportunities in {state.region}."
                )
            else:
                summary = (
                    f"**Document Processed**\n\n"
                    f"Successfully extracted text from {len(pdf_reader.pages)} page(s). "
                    f"Document content analyzed for insights related to {state.molecule} "
                    f"in {state.region}."
                )
            
            # Store extracted text as raw reference
            raw_refs = [{"type": "pdf_extract", "pages": len(pdf_reader.pages), "preview": full_text[:500]}]
            
        except Exception as e:
            summary = (
                f"**Document Processing Error**\n\n"
                f"Could not process uploaded PDF: {str(e)}. "
                f"Falling back to mock insights."
            )
            raw_refs = []
    else:
        # No file uploaded or PDF library not available - use mock insights
        if not state.uploaded_doc:
            summary = (
                "**No Document Uploaded**\n\n"
                "Mock internal strategy decks highlight adherence issues and access gaps "
                "for LAMA inhalers, suggesting opportunity in device innovation and "
                "patient education programs. Upload a PDF document to analyze actual internal insights."
            )
        else:
            summary = (
                "**PDF Processing Unavailable**\n\n"
                "PyPDF2 library not installed. Install it with: pip install PyPDF2. "
                "Using mock insights for now."
            )
        raw_refs = []
    
    state.agent_results["internal"] = AgentResult(
        agent_name="Internal Insights Agent",
        summary=summary,
        raw_refs=raw_refs,
    )
    return state


def web_intelligence_agent(state: ConversationState) -> ConversationState:
    # Check if this agent should run
    if not any(task.get("agent") == "web" for task in state.tasks):
        return state
    
    json_path = DATA_DIR / "web_results.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    hits = data.get("tiotropium_unmet_need", []) if state.molecule.lower() == "tiotropium".lower() else []

    if not hits:
        summary = (
            f"**Web Intelligence Not Configured**\n\n"
            f"No mock web snippets configured for {state.molecule}. "
            f"In a production system, this agent would perform real-time web searches on: "
            f"PubMed, clinical guidelines (GINA, GOLD), regulatory databases (FDA, EMA), "
            f"and real-world evidence sources to find relevant information."
        )
    else:
        summary = (
            "Mock web and guideline snippets indicate persistent symptoms and "
            "poor inhaler technique in COPD patients on tiotropium, and "
            "underutilisation in severe asthma despite evidence of benefit."
        )

    state.agent_results["web"] = AgentResult(
        agent_name="Web Intelligence Agent",
        summary=summary,
        raw_refs=hits,
    )
    return state


