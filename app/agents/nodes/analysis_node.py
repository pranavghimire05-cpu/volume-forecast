from collections import defaultdict
from statistics import mean


def safe_variance_pct(value, average):
    """Percentage difference from average, returns 0.0 if average is 0."""
    if average == 0:
        return 0.0
    return round(((value - average) / average) * 100, 2)


def performance_feature_engineering_node(state):
    rows = state.get("db_rows", [])

    if not rows:
        return {"employee_features": []}

    employee_features = []

    # Group employees by role
    role_groups = defaultdict(list)
    for row in rows:
        role_groups[row["role"]].append(row)

    # Calculate role benchmarks
    role_benchmarks = {}
    for role, employees in role_groups.items():
        role_benchmarks[role] = {
            "avg_mph":      mean(e["mph"]      for e in employees),
            "avg_rph":      mean(e["rph"]      for e in employees),
            "avg_accuracy": mean(e["accuracy"] for e in employees),
            "avg_rating":   mean(e["rating"]   for e in employees),
        }

    # Build employee profiles
    for role, employees in role_groups.items():
        benchmark = role_benchmarks[role]

        ranked_employees = sorted(
            employees,
            key=lambda x: (x["accuracy"], x["mph"], x["rating"]),
            reverse=True
        )

        total = len(ranked_employees)

        for rank, emp in enumerate(ranked_employees, start=1):

            performance_score = round(
                emp["mph"]      * 0.30
                + emp["rph"]    * 0.20
                + emp["accuracy"] * 0.30
                + emp["rating"] * 10 * 0.20,
                2
            )

            # Variances
            mph_var      = round(emp["mph"]      - benchmark["avg_mph"],      2)
            rph_var      = round(emp["rph"]      - benchmark["avg_rph"],      2)
            acc_var      = round(emp["accuracy"] - benchmark["avg_accuracy"], 2)
            rating_var   = round(emp["rating"]   - benchmark["avg_rating"],   2)

            # Variance percents — safe division
            mph_var_pct      = safe_variance_pct(emp["mph"],      benchmark["avg_mph"])
            rph_var_pct      = safe_variance_pct(emp["rph"],      benchmark["avg_rph"])
            acc_var_pct      = safe_variance_pct(emp["accuracy"], benchmark["avg_accuracy"])
            rating_var_pct   = safe_variance_pct(emp["rating"],   benchmark["avg_rating"])

            employee_features.append({
                "id":   emp["id"],
                "name": emp["name"],
                "role": emp["role"],

                # Raw metrics
                "mph":      emp["mph"],
                "rph":      emp["rph"],
                "accuracy": emp["accuracy"],
                "rating":   emp["rating"],

                # Role benchmarks
                "role_avg_mph":      round(benchmark["avg_mph"],      2),
                "role_avg_rph":      round(benchmark["avg_rph"],      2),
                "role_avg_accuracy": round(benchmark["avg_accuracy"], 2),
                "role_avg_rating":   round(benchmark["avg_rating"],   2),

                # Variance from benchmark (absolute)
                "mph_vs_role_avg":      mph_var,
                "rph_vs_role_avg":      rph_var,
                "accuracy_vs_role_avg": acc_var,
                "rating_vs_role_avg":   rating_var,

                # Variance from benchmark (percent) ← fixes NaN/Inf
                "mph_vs_role_avg_pct":      mph_var_pct,
                "rph_vs_role_avg_pct":      rph_var_pct,
                "accuracy_vs_role_avg_pct": acc_var_pct,
                "rating_vs_role_avg_pct":   rating_var_pct,

                # Ranking
                "rank_in_role":  rank,
                "total_in_role": total,
                "percentile":    round(((total - rank + 1) / total) * 100, 2),

                # Boolean flags
                "above_avg_mph":      emp["mph"]      > benchmark["avg_mph"],
                "above_avg_rph":      emp["rph"]      > benchmark["avg_rph"],
                "above_avg_accuracy": emp["accuracy"] > benchmark["avg_accuracy"],
                "above_avg_rating":   emp["rating"]   > benchmark["avg_rating"],
                "high_accuracy":      emp["accuracy"] >= 98,
                "low_accuracy":       emp["accuracy"] <  95,
                "top_rated":          emp["rating"]   >= 4.5,

                # Composite score
                "performance_score": performance_score,
            })

    return {"employee_features": employee_features}