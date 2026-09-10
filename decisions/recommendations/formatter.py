from decisions.criteria.models import FinalRecommendation

def format_decision_report(recommendation: FinalRecommendation) -> str:
    """Transforms the decision data into a structured Markdown report for the UI."""
    report = f"## Decision Recommendation: {recommendation.recommended_option}\n\n"
    report += f"**Research Objective:** {recommendation.research_objective}\n"
    report += f"**Overall Confidence:** {recommendation.overall_confidence * 100:.0f}%\n\n"
    
    report += "### Trade-off Analysis\n"
    report += f"{recommendation.trade_off_analysis}\n\n"
    
    report += "### Criteria Comparison\n"
    report += "| Option | Total Score | Uncertainty Flags |\n"
    report += "|---|---|---|\n"
    
    for opt in recommendation.alternatives_compared:
        flags_count = len(opt.uncertainty_flags)
        report += f"| **{opt.option_name}** | {opt.total_weighted_score} | {flags_count} |\n"
        
    return report