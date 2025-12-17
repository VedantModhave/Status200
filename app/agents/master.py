from typing import Dict, Any, List, Optional

from .state import ConversationState, AgentResult


def plan_tasks(state: ConversationState) -> ConversationState:
    """
    Query-aware task planner that selects relevant agents based on query intent.
    """
    query_lower = state.user_query.lower()
    
    # Define agent keywords for intelligent routing
    agent_keywords = {
        "iqvia": ["market", "sales", "growth", "cagr", "competition", "competitor", "revenue", "size", "trend"],
        "exim": ["import", "export", "trade", "exim", "supply", "sourcing", "api", "formulation", "volume"],
        "patent": ["patent", "ip", "intellectual property", "expiry", "fto", "freedom to operate", "filing"],
        "clinical_trials": ["trial", "clinical", "pipeline", "phase", "study", "sponsor", "recruiting", "nct"],
        "internal": ["internal", "strategy", "field", "mins", "deck", "insight"],
        "web": ["guideline", "publication", "literature", "rwe", "real world", "evidence", "journal", "news"],
    }
    
    # Determine which agents to run based on query
    selected_agents = []
    
    # If query is very generic (like "find opportunities"), run all agents
    generic_queries = ["opportunity", "innovation", "find", "identify", "explore", "analyze", "summary", "complete", "all", "everything"]
    is_generic = any(gq in query_lower for gq in generic_queries) and len(query_lower.split()) < 15
    
    if is_generic:
        # Run all agents for comprehensive analysis
        selected_agents = ["iqvia", "exim", "patent", "clinical_trials", "internal", "web"]
    else:
        # Select agents based on keywords
        for agent_name, keywords in agent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                selected_agents.append(agent_name)
        
        # If no specific matches, default to core agents (run most agents for better demo)
        if not selected_agents:
            selected_agents = ["iqvia", "exim", "patent", "clinical_trials", "web"]
    
    # Build task list
    tasks = []
    for agent in selected_agents:
        task_type_map = {
            "iqvia": "market_insights",
            "exim": "trade_trends",
            "patent": "patent_landscape",
            "clinical_trials": "trial_pipeline",
            "internal": "internal_insights",
            "web": "web_intel",
        }
        tasks.append({"agent": agent, "task_type": task_type_map.get(agent, "general")})
    
    state.tasks = tasks
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


