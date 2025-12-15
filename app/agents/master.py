from typing import Dict, Any, List, Optional

from .state import ConversationState, AgentResult


def plan_tasks(state: ConversationState) -> ConversationState:
    """
    Simple, rule-based planner for now.
    Later this will be LLM-driven within LangGraph.
    """
    base_tasks: List[Dict[str, Any]] = [
        {"agent": "iqvia", "task_type": "market_insights"},
        {"agent": "exim", "task_type": "trade_trends"},
        {"agent": "patent", "task_type": "patent_landscape"},
        {"agent": "clinical_trials", "task_type": "trial_pipeline"},
        {"agent": "internal", "task_type": "internal_insights"},
        {"agent": "web", "task_type": "web_intel"},
    ]
    state.tasks = base_tasks
    return state


def synthesize_results(state: ConversationState) -> ConversationState:
    """
    Simple rule-based synthesis to highlight whitespace and opportunities.
    """
    parts: List[str] = []
    parts.append(
        f"Synthesizing findings for **{state.molecule}** in **{state.region}** "
        f"over **{state.time_horizon}**."
    )

    # Derive some simple metrics from agent tables
    iqvia = state.agent_results.get("iqvia")
    trials = state.agent_results.get("clinical_trials")
    patents = state.agent_results.get("patent")

    whitespace_flags: List[str] = []
    opp_flags: List[str] = []

    # Clinical whitespace: high market, few active trials
    active_trials = 0
    if trials and trials.tables:
        rows = trials.tables[0].get("rows", [])
        active_trials = sum(
            1
            for r in rows
            if str(r.get("status")) in ("Active", "Recruiting")
        )

    est_market: Optional[float] = None
    if iqvia and iqvia.tables:
        rows = iqvia.tables[0].get("rows", [])
        if rows:
            latest = sorted(rows, key=lambda r: r.get("year", 0))[-1]
            est_market = float(latest.get("market_size_usd_mn", 0.0))

    if est_market and est_market >= 100 and active_trials <= 2:
        whitespace_flags.append(
            f"High-value but under-explored market: estimated market size ~USD {est_market:.0f}m "
            f"with only {active_trials} active/recruiting trials in the mock pipeline."
        )

    # Patent-driven opportunity: expiry within 2 years
    if patents and patents.tables:
        rows = patents.tables[0].get("rows", [])
        if rows:
            soon = sorted(rows, key=lambda r: r.get("expiry_year", 9999))[0]
            years_to_expiry = soon.get("expiry_year", 9999) - 2025
            if years_to_expiry <= 2:
                opp_flags.append(
                    f"Key patent {soon.get('patent_no')} ({soon.get('patent_type')}) "
                    f"expires in {soon.get('expiry_year')}, suggesting a window for "
                    "biosimilars or differentiated formulations."
                )

    if whitespace_flags or opp_flags:
        parts.append("")
        parts.append("**Strategic Signals**")
        for w in whitespace_flags:
            parts.append(f"- 🔍 Whitespace: {w}")
        for o in opp_flags:
            parts.append(f"- 💡 Opportunity: {o}")

    parts.append("")
    parts.append("**Agent Findings**")
    for agent_name, result in state.agent_results.items():
        parts.append(f"- **{result.agent_name}**: {result.summary}")

    if not state.agent_results:
        parts.append(
            "No agent results available yet. This is a placeholder summary."
        )

    state.final_summary = "\n".join(parts)
    return state


