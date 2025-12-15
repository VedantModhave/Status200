import json
from pathlib import Path

import pandas as pd

from .state import ConversationState, AgentResult

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def iqvia_insights_agent(state: ConversationState) -> ConversationState:
    csv_path = DATA_DIR / "iqvia_markets.csv"
    df = pd.read_csv(csv_path)
    df_filt = df[(df["molecule"] == state.molecule) & (df["country"] == state.region)]

    if df_filt.empty:
        summary = (
            f"No IQVIA mock data found for {state.molecule} in {state.region}. "
            "In a real system, this would fall back to a broader geography."
        )
        tables = []
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

    state.agent_results["iqvia"] = AgentResult(
        agent_name="IQVIA Insights Agent",
        summary=summary,
        tables=tables,
    )
    return state


def exim_trade_agent(state: ConversationState) -> ConversationState:
    csv_path = DATA_DIR / "exim_trade.csv"
    df = pd.read_csv(csv_path)
    df_filt = df[(df["molecule"] == state.molecule) & (df["country"] == state.region)]

    if df_filt.empty:
        summary = (
            f"No EXIM trade data found for {state.molecule} in {state.region}."
        )
        tables = []
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

    state.agent_results["exim"] = AgentResult(
        agent_name="EXIM Trade Agent",
        summary=summary,
        tables=tables,
    )
    return state


def patent_landscape_agent(state: ConversationState) -> ConversationState:
    json_path = DATA_DIR / "patents.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    relevant = [p for p in data if p["molecule"] == state.molecule]

    if not relevant:
        summary = f"No mock patent records found for {state.molecule}."
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
    csv_path = DATA_DIR / "clinical_trials.csv"
    df = pd.read_csv(csv_path)
    df_filt = df[(df["molecule"] == state.molecule) & (df["country"] == state.region)]

    if df_filt.empty:
        summary = (
            f"No clinical trial records found for {state.molecule} in {state.region} "
            "in the mock dataset."
        )
        tables = []
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

    state.agent_results["clinical_trials"] = AgentResult(
        agent_name="Clinical Trials Agent",
        summary=summary,
        tables=tables,
    )
    return state


def internal_insights_agent(state: ConversationState) -> ConversationState:
    # For now we keep this high-level; later we can plug in PDF/RAG.
    summary = (
        "Mock internal strategy decks highlight adherence issues and access gaps "
        "for LAMA inhalers, suggesting opportunity in device innovation and "
        "patient education programs."
    )
    state.agent_results["internal"] = AgentResult(
        agent_name="Internal Insights Agent",
        summary=summary,
    )
    return state


def web_intelligence_agent(state: ConversationState) -> ConversationState:
    json_path = DATA_DIR / "web_results.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    hits = data.get("tiotropium_unmet_need", []) if state.molecule.lower() == "tiotropium".lower() else []

    if not hits:
        summary = (
            f"No mock web snippets configured for {state.molecule}. "
            "In a real system, this agent would query guidelines and RWE sources."
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


