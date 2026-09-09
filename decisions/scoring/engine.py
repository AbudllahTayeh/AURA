from typing import List
from decisions.criteria.models import AlternativeOption, DecisionCriterion

def calculate_weighted_scores(
    options: List[AlternativeOption], criteria: List[DecisionCriterion]
) -> List[AlternativeOption]:
    """Applies criteria weights to normalized scores for each alternative."""
    weight_map = {c.name: c.weight for c in criteria}

    for option in options:
        total_score = 0.0
        for score in option.scores:
            weight = weight_map.get(score.criterion_name, 0.0)
            total_score += score.normalized_score * weight
        option.total_weighted_score = round(total_score, 2)

    return sorted(options, key=lambda x: x.total_weighted_score, reverse=True)
