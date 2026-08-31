def calculate_health_score(
    security_issues,
    cycles,
    complexity_results,
    unused_functions
):
    score = 100

    # Security penalties
    for issue in security_issues:
        if issue["severity"] == "HIGH":
            score -= 15
        elif issue["severity"] == "MEDIUM":
            score -= 7

    # Circular dependency penalty
    score -= len(cycles) * 10

    # Complexity penalty
    for function in complexity_results:
        if function["complexity"] > 10:
            score -= 5

    # Dead code penalty
    score -= len(unused_functions) * 2

    # Keep score between 0 and 100
    score = max(0, min(100, score))

    if score >= 90:
        grade = "EXCELLENT"
    elif score >= 75:
        grade = "GOOD"
    elif score >= 50:
        grade = "FAIR"
    else:
        grade = "POOR"

    return {
        "score": score,
        "grade": grade
    }