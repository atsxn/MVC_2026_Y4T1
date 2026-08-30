def score_ballots(ballots, candidates, points):
    """Sum ranking points over the given ballots.

    Every candidate is present in the result, including the ones nobody ranked.
    """
    scores = {candidate.id: 0 for candidate in candidates}
    for ballot in ballots:
        for position, candidate_id in enumerate(ballot.ranking):
            if position < len(points) and candidate_id in scores:
                scores[candidate_id] += points[position]
    return scores
