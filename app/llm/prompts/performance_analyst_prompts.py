from app.llm.prompts.prompts_builder import build_prompt


def build_performance_analyst_prompt(employees: list[dict]) -> str:
    rows = "\n".join(
        f"{e['id']}|{e.get('role')}|score={e.get('performance_score')}|pct={e.get('percentile')}|"
        f"mph={e.get('mph_vs_role_avg_pct', 0):+.0f}%|rph={e.get('rph_vs_role_avg_pct', 0):+.0f}%|"
        f"acc={e.get('accuracy_vs_role_avg_pct', 0):+.0f}%|rating={e.get('rating_vs_role_avg_pct', 0):+.0f}%|"
        f"flags={'T' if e.get('top_rated') else ''}{'H' if e.get('high_accuracy') else ''}{'L' if e.get('low_accuracy') else ''}"
        for e in employees
    )
    return build_prompt(
        role="Performance Analyst",
        objective="For each employee row below, generate qualitative performance insights.",
        context=f"Format: id|role|score|percentile|mph%|rph%|acc%|rating%|flags\n\n{rows}",
        instructions="""
Each row has an explicit id= field. For EVERY row, return one object whose "id" field
exactly matches that row's id= value, plus:
performance_tier, capacity_signal, quality_signal, burnout_signal, deployment_score,
suitability_profile, recommendation, key_strengths (max 2, <=5 words each),
improvement_areas (max 2, <=5 words each), executive_summary (1 sentence).

Return exactly one object per input row, in the same order, using the same id value.
Do not skip any row. Do not invent ids. Do not invent numbers — base all judgments
only on the data given.
""")