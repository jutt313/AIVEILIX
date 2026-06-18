"""
Agent harness — the rebuilt tool-calling brain.

The harness reasons before acting, carries state across the turn, narrates
its work in plain language, and never leaks internals. Document pipeline,
retrieval, embeddings, Qdrant, and storage are not touched — only the
agent brain (this folder) is new.

Entry point: AgentRunner.run(TurnInput, on_event=...) -> TurnOutput
"""

from app.services.agent.harness.contract import TurnInput, TurnOutput
from app.services.agent.harness.runner import AgentRunner, run_turn
from app.services.agent.harness.state import AgentState, PlanItem, PlanStatus

__all__ = [
    "AgentRunner",
    "AgentState",
    "PlanItem",
    "PlanStatus",
    "TurnInput",
    "TurnOutput",
    "run_turn",
]
