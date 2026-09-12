from decisions.criteria.models import FinalRecommendation


def format_decision_report(recommendation: FinalRecommendation) -> str:
    """Transforms the decision data into a structured Markdown report for the UI."""
    report = f"## Decision Recommendation: {recommendation.recommended_option}\n\n"
    report += f"**Research Objective:** {recommendation.research_objective}\n"
    report += (
        f"**Overall Confidence:** {recommendation.overall_confidence * 100:.0f}%\n\n"
    )

    report += "### Trade-off Analysis\n"
    report += f"{recommendation.trade_off_analysis}\n\n"

    if not recommendation.alternatives_compared:
        return report

    # 1. Multi-Alternative Criteria Comparison Matrix (docs/README.md Section 10)
    if recommendation.criteria_used:
        report += "### Criteria Comparison Matrix\n"
        headers = ["Criterion", "Weight"] + [
            opt.option_name for opt in recommendation.alternatives_compared
        ]
        report += "| " + " | ".join(headers) + " |\n"
        report += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        for crit in recommendation.criteria_used:
            weight_str = (
                f"{crit.weight * 100:.0f}%"
                if crit.weight <= 1.0
                else f"{crit.weight:.1f}"
            )
            row = [f"**{crit.name}**", weight_str]
            for opt in recommendation.alternatives_compared:
                matching_score = next(
                    (
                        s
                        for s in opt.scores
                        if s.criterion_name.lower() == crit.name.lower()
                    ),
                    None,
                )
                if matching_score:
                    row.append(f"{matching_score.normalized_score:.1f}/10")
                else:
                    row.append("-")
            report += "| " + " | ".join(row) + " |\n"

        # Summary total row
        total_row = ["**Total Weighted Score**", "100%"] + [
            f"**{opt.total_weighted_score:.1f}**"
            for opt in recommendation.alternatives_compared
        ]
        report += "| " + " | ".join(total_row) + " |\n\n"

    # 2. Ranking & Uncertainty Overview Table
    report += "### Ranking & Uncertainty Overview\n"
    report += "| Option | Total Score | Uncertainty Flags |\n"
    report += "|---|---|---|\n"
    for opt in recommendation.alternatives_compared:
        flags_count = len(opt.uncertainty_flags)
        report += (
            f"| **{opt.option_name}** | {opt.total_weighted_score} | {flags_count} |\n"
        )
    report += "\n"

    # 3. Evidence & Citation Traceability (docs/README.md Section 10)
    report += "### Evidence & Citation Traceability\n"
    for opt in recommendation.alternatives_compared:
        report += f"#### {opt.option_name}\n"
        if not opt.scores:
            report += "_No criterion scores recorded._\n\n"
            continue

        for score in opt.scores:
            citations_str = (
                ", ".join(score.citation_ids) if score.citation_ids else "No citations"
            )
            report += (
                f"- **{score.criterion_name}** ({score.normalized_score:.1f}/10) "
                f"[{score.claim_state}]: {score.evidence_summary} "
                f"*(Citations: {citations_str})*\n"
            )

        if opt.uncertainty_flags:
            flags_str = "; ".join(opt.uncertainty_flags)
            report += f"- ⚠️ **Uncertainty Flags**: {flags_str}\n"

        report += "\n"

    return report
