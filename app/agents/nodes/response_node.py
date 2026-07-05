from app.agents.state import AgentState
from app.llm.prompts.performance_analyst_prompts import build_performance_analyst_prompt
from app.llm.schema.performance_analyst_schema import (
    EmployeePerformanceAnalysis,
    LLMPerformanceInsightsBatch,
    MetricComparison,
    BenchmarkAnalysis,
    WorkforceFlags,
)
from itertools import islice


def chunked(iterable, size):
    it = iter(iterable)
    while batch := list(islice(it, size)):
        yield batch


def build_benchmark_analysis(emp: dict) -> BenchmarkAnalysis:
    def mc(key, avg_key, var_key, var_pct_key, above_key):
        return MetricComparison(
            metric_name=key,
            employee_value=emp.get(key, 0.0),
            role_average=emp.get(avg_key, 0.0),
            variance=emp.get(var_key, 0.0),
            variance_percent=emp.get(var_pct_key, 0.0),
            above_average=emp.get(above_key, False),
        )
    return BenchmarkAnalysis(
        mph=mc("mph", "role_avg_mph", "mph_vs_role_avg", "mph_vs_role_avg_pct", "above_avg_mph"),
        rph=mc("rph", "role_avg_rph", "rph_vs_role_avg", "rph_vs_role_avg_pct", "above_avg_rph"),
        accuracy=mc("accuracy", "role_avg_accuracy", "accuracy_vs_role_avg", "accuracy_vs_role_avg_pct", "above_avg_accuracy"),
        rating=mc("rating", "role_avg_rating", "rating_vs_role_avg", "rating_vs_role_avg_pct", "above_avg_rating"),
    )


def build_workforce_flags(emp: dict) -> WorkforceFlags:
    return WorkforceFlags(
        top_rated=emp.get("top_rated", False),
        mentor_candidate=False,
        promotion_candidate=False,
        reallocation_candidate=False,
        coaching_candidate=False,
    )


async def response_node(state: AgentState, llm) -> AgentState:
    employee_features = state.get("employee_features", [])

    if not employee_features:
        state["final_response"] = []
        return state

    structured_llm = llm.with_structured_output(LLMPerformanceInsightsBatch)

    BATCH_SIZE = 12
    batches = list(chunked(employee_features, BATCH_SIZE))
    prompts = [build_performance_analyst_prompt(b) for b in batches]

    batch_responses = []
    for i, prompt in enumerate(prompts):
        try:
            resp = await structured_llm.ainvoke(prompt)
            batch_responses.append(resp)
        except Exception as e:
            print(f"[performance_analyst] batch {i} failed: {e}")
            batch_responses.append(LLMPerformanceInsightsBatch(results=[]))

    insights_by_id = {
        item.id: item
        for resp in batch_responses
        for item in resp.results
    }

    results = []
    missing_ids = []

    for emp in employee_features:
        insights = insights_by_id.get(emp["id"])
        if insights is None:
            missing_ids.append(emp["id"])
            continue

        analysis = EmployeePerformanceAnalysis(
            id=emp["id"],
            employee_name=emp["name"],
            role=emp["role"],
            performance_score=emp.get("performance_score", 0.0),
            performance_tier=insights.performance_tier,
            rank_in_role=emp["rank_in_role"],
            total_in_role=emp["total_in_role"],
            percentile=emp.get("percentile", 0.0),
            raw_mph=emp.get("mph", 0.0),
            raw_rph=emp.get("rph", 0.0),
            raw_accuracy=emp.get("accuracy", 0.0),
            raw_rating=emp.get("rating", 0.0),
            benchmark_analysis=build_benchmark_analysis(emp),
            capacity_signal=insights.capacity_signal,
            quality_signal=insights.quality_signal,
            burnout_signal=insights.burnout_signal,
            deployment_score=insights.deployment_score,
            suitability_profile=insights.suitability_profile,
            workforce_flags=build_workforce_flags(emp),
            recommendation=insights.recommendation,
            key_strengths=insights.key_strengths,
            improvement_areas=insights.improvement_areas,
            executive_summary=insights.executive_summary,
        )
        results.append(analysis)

    if missing_ids:
        print(f"[performance_analyst] missing insights for: {missing_ids}")

    state["final_response"] = results
    return state
