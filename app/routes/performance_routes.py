from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.db.database import get_db
from app.llm.model.mistral_ai import get_llm
from sqlalchemy.orm import Session
from app.agents.graph import build_graph
from app.services.performance.performance_service import process_performance_file
from app.llm.schema.performance_analyst_schema import EmployeePerformanceAnalysis
import math

router = APIRouter(prefix="/performance", tags=["preformance"])


def sanitize_floats(obj):
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: sanitize_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_floats(i) for i in obj]
    return obj


@router.get("/")
def get_health():
    return {"status": "healthy"}


@router.post("/")
async def upload_performance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await process_performance_file(file, db)


    
@router.get("/run")
async def run_agent(
    query: str,
    db: Session = Depends(get_db)
):
    llm = get_llm()
    graph = build_graph(db, llm)

    result = await graph.ainvoke({"query": query})

    final_response = result.get("final_response", [])

    # Serialize list of EmployeePerformanceAnalysis objects
    if isinstance(final_response, list):
        serialized = [
            sanitize_floats(item.model_dump())
            if isinstance(item, EmployeePerformanceAnalysis)
            else item
            for item in final_response
        ]
        return JSONResponse(content=serialized)

    # Fallback for single object
    if isinstance(final_response, EmployeePerformanceAnalysis):
        return JSONResponse(content=sanitize_floats(final_response.model_dump()))

    return JSONResponse(content=final_response)




