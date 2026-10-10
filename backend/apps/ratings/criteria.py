"""Allowed rating dimensions keyed by the role of the participant being reviewed."""

RATING_DIMENSIONS = {
    "seller": {"product_quality", "quantity_accuracy", "delivery", "communication", "documentation"},
    "buyer": {"payment_reliability", "communication", "order_accuracy", "acceptance_process"},
    "logistics": {"on_time_delivery", "cargo_handling", "tracking", "communication"},
    "inspector": {"inspection_quality", "report_accuracy", "timeliness", "professionalism"},
}


def validate_dimensions(role, dimensions):
    if not isinstance(dimensions, dict):
        return "Dimensions must be a JSON object mapping criterion names to scores."
    allowed = RATING_DIMENSIONS.get(role, set())
    if not allowed:
        return f"Ratings for role '{role}' are not supported yet."
    unknown = set(dimensions) - allowed
    if unknown:
        return f"Unsupported rating dimensions for {role}: {', '.join(sorted(unknown))}."
    if not dimensions:
        return "Provide at least one rating dimension."
    for key, score in dimensions.items():
        if isinstance(score, bool) or not isinstance(score, (int, float)) or score < 1 or score > 5:
            return f"Dimension '{key}' must have a score from 1 to 5."
        if int(score) != score:
            return f"Dimension '{key}' must be a whole-number score from 1 to 5."
    return None
