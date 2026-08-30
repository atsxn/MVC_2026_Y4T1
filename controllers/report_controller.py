from models.ballot import BallotStatus


class ReportController:
    """Read only view of the election for the status and result screens."""
    # STATUS ... RESULT
    def __init__(self, election):
        self.election = election

    def snapshot(self):
        election = self.election
        return {
            "title": election.title,
            "status": election.status,
            "accepted": len(election.ballots),
            "certified": len(election.counted_ballots()),
            "rejected": len(election.rejected_ballots()),
            "under_review": len(election.under_review_ballots()),
            "groups": election.groups,
            "scores": election.scores(),
            "candidates": election.candidates,
        }

    def audit_rows(self):
        """One row per ballot: who cast it, how it was ranked, where it ended up..."""
        rows = []
        for ballot in self.election.ballots:
            rows.append({
                "ballot_id": ballot.id,
                "voter_id": ballot.voter_id,
                "ranking": ballot.ranking,
                "status": ballot.status,
                "group_id": ballot.group_id or "-",
            })
        return rows

    def candidate_name(self, candidate_id):
        return self.election.candidate_name(candidate_id)

    def pattern_text(self, pattern):
        return " > ".join(pattern)

    def status_label(self, status):
        return status.value if isinstance(status, BallotStatus) else str(status)
