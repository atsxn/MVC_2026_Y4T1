from enum import Enum


class GroupDecision(Enum):
    PENDING = "Pending review"
    APPROVED = "Approved"
    REJECTED = "Not counted"


class PatternGroup:
    # group ballots with same pattern for officer to review
    def __init__(self, group_id, pattern, ballot_ids):
        self.id = group_id
        self.pattern = tuple(pattern)
        self.ballot_ids = list(ballot_ids)
        self.decision = GroupDecision.PENDING

    @property
    def size(self):
        return len(self.ballot_ids)

    def is_pending(self):
        return self.decision is GroupDecision.PENDING
