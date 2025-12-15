"""
LangGraph workflow for the EY Pharma demo.

We wrap existing planner/worker/synthesis logic into a simple LangGraph graph.
"""

from typing import Callable, TypedDict

from langgraph.graph import StateGraph, END

from agents.state import ConversationState
from agents import master, workers
from agents.report import generate_pdf_report


class WorkflowState(TypedDict, total=False):
    user_query: str
    molecule: str
    region: str
    time_horizon: str
    tasks: list
    agent_results: dict
    final_summary: str
    report_path: str


def _to_model(state: WorkflowState) -> ConversationState:
    return ConversationState(
        user_query=state.get("user_query", ""),
        molecule=state.get("molecule", ""),
        region=state.get("region", ""),
        time_horizon=state.get("time_horizon", ""),
        tasks=state.get("tasks", []) or [],
        agent_results=state.get("agent_results", {}) or {},
        final_summary=state.get("final_summary"),
        report_path=state.get("report_path"),
    )


def _from_model(model: ConversationState, state: WorkflowState) -> WorkflowState:
    state["user_query"] = model.user_query
    state["molecule"] = model.molecule
    state["region"] = model.region
    state["time_horizon"] = model.time_horizon
    state["tasks"] = model.tasks
    state["agent_results"] = model.agent_results
    state["final_summary"] = model.final_summary or ""
    state["report_path"] = model.report_path
    return state


def node_plan(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = master.plan_tasks(cs)
    return _from_model(cs, state)


def node_iqvia(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = workers.iqvia_insights_agent(cs)
    return _from_model(cs, state)


def node_exim(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = workers.exim_trade_agent(cs)
    return _from_model(cs, state)


def node_patent(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = workers.patent_landscape_agent(cs)
    return _from_model(cs, state)


def node_clinical(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = workers.clinical_trials_agent(cs)
    return _from_model(cs, state)


def node_internal(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = workers.internal_insights_agent(cs)
    return _from_model(cs, state)


def node_web(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = workers.web_intelligence_agent(cs)
    return _from_model(cs, state)


def node_synthesis(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    cs = master.synthesize_results(cs)
    return _from_model(cs, state)


def node_report(state: WorkflowState) -> WorkflowState:
    cs = _to_model(state)
    path = generate_pdf_report(cs)
    cs.report_path = path
    return _from_model(cs, state)


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("plan", node_plan)
    graph.add_node("iqvia", node_iqvia)
    graph.add_node("exim", node_exim)
    graph.add_node("patent", node_patent)
    graph.add_node("clinical", node_clinical)
    graph.add_node("internal", node_internal)
    graph.add_node("web", node_web)
    graph.add_node("synthesis", node_synthesis)
    graph.add_node("report", node_report)

    graph.set_entry_point("plan")
    # Simple linear flow for now (can be parallelised later)
    graph.add_edge("plan", "iqvia")
    graph.add_edge("iqvia", "exim")
    graph.add_edge("exim", "patent")
    graph.add_edge("patent", "clinical")
    graph.add_edge("clinical", "internal")
    graph.add_edge("internal", "web")
    graph.add_edge("web", "synthesis")
    graph.add_edge("synthesis", "report")
    graph.add_edge("report", END)

    return graph.compile()


def run_demo_workflow(
    user_query: str, molecule: str, region: str, time_horizon: str
) -> ConversationState:
    """
    Run the LangGraph workflow and return a ConversationState instance.
    """
    app = build_graph()
    initial: WorkflowState = {
        "user_query": user_query,
        "molecule": molecule,
        "region": region,
        "time_horizon": time_horizon,
    }
    final_state: WorkflowState = app.invoke(initial)
    return _to_model(final_state)



