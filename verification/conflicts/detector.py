from verification.claims.models import Evidence


def detect_conflicts(evidence_list: list[Evidence]) -> list[tuple[Evidence, Evidence]]:
    """
    Very simple placeholder conflict detector.

    Flags two pieces of evidence as conflicting if they share
    significant word overlap (meaning they likely discuss the
    same topic) but contain opposite polarity words
    (e.g. one has "free"/"supports" and the other has
    "paid"/"does not support"/"requires").

    This is a naive first version. Later this should be replaced
    with a real natural language inference (NLI) model that can
    detect contradiction, entailment, and neutrality properly.
    """
    negative_markers = {
        "not", "no", "never", "cannot", "can't", "doesn't",
        "does", "requires", "paid", "unsupported", "lacks",
    }

    conflicts: list[tuple[Evidence, Evidence]] = []

    for i in range(len(evidence_list)):
        for j in range(i + 1, len(evidence_list)):
            ev_a = evidence_list[i]
            ev_b = evidence_list[j]

            words_a = set(ev_a.text.lower().split())
            words_b = set(ev_b.text.lower().split())

            # Are they even talking about the same topic?
            shared_words = words_a & words_b
            if len(shared_words) < 2:
                continue  # probably unrelated, skip

            a_has_negative = bool(words_a & negative_markers)
            b_has_negative = bool(words_b & negative_markers)

            # Conflict signal: one text has negative/limiting
            # language and the other doesn't, despite discussing
            # the same topic.
            if a_has_negative != b_has_negative:
                conflicts.append((ev_a, ev_b))

    return conflicts