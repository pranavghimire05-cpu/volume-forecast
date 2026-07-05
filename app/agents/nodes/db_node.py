# agents/nodes/db_node.py

from app.agents.state import AgentState
from app.services.performance.performance_query import get_all_performance_rows

def db_node(state: AgentState, db_session) -> AgentState:
    query = state["query"]

    rows = get_all_performance_rows(
        db=db_session,
        limit=50,
    )

    state["db_rows"] = rows
    return state