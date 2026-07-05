# agents/graph.py
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes.db_node import db_node
from app.agents.nodes.analysis_node import performance_feature_engineering_node
from app.agents.nodes.response_node import response_node


def build_graph(session, llm):

    graph = StateGraph(AgentState)

    # wrapper functions to inject dependencies
    def db_wrapper(state):
        return db_node(state, session)

    async def response_wrapper(state):
        return await response_node(state, llm)

    # nodes
    graph.add_node("db", db_wrapper)
    graph.add_node("analysis", performance_feature_engineering_node)
    graph.add_node("response", response_wrapper)

    # edges
    graph.set_entry_point("db")
    graph.add_edge("db", "analysis")
    graph.add_edge("analysis", "response")
    graph.add_edge("response", END)

    return graph.compile()