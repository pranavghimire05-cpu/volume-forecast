from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    query: str
    db_rows: List[Dict[str, Any]]
    employee_features: List[Dict[str, Any]] 
    insights: Dict[str, Any]
    final_response: Any  