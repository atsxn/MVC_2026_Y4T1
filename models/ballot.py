from enum import Enum


class BallotStatus(Enum):
    RECORDED = "Recorded"
    UNDER_REVIEW = "Under review"
    CERTIFIED = "Certified"
    REJECTED = "Not counted"


class Ballot:
    def __init__(self, ballot_id, voter_id, ranking):
        self.id = ballot_id
        self.voter_id = voter_id
        self.ranking = tuple(ranking)
        self.status = BallotStatus.RECORDED
        self.group_id = None

    @property
    def pattern(self):
        # return ranking as pattern
        return self.ranking

    def is_counted(self):
        return self.status is BallotStatus.CERTIFIED

    def __repr__(self):
        return "Ballot(%s, %s, %s)" % (self.id, self.voter_id, self.status.name)
