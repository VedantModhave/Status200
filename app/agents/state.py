from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    agent_name: str
    summary: str
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    raw_refs: List[Dict[str, Any]] = Field(default_factory=list)


class ConversationState(BaseModel):
    """
    Shared state that flows through the LangGraph workflow.
    """

    user_query: str
    molecule: str
    region: str
    time_horizon: str

    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    agent_results: Dict[str, AgentResult] = Field(default_factory=dict)

    final_summary: Optional[str] = None
    report_path: Optional[str] = None


