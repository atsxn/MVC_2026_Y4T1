from models.errors import RuleViolation

from .result import Result


class OfficerController:
    # handle officer tasks like closing vote and reviewing groups

    def __init__(self, election):
        self.election = election

    def close_voting(self):
        try:
            pending = self.election.close_voting()
        except RuleViolation as exc:
            return Result.failure(str(exc))
        message = "Voting closed. %d repeated pattern group(s) need review" % len(pending)
        return Result.success(message, pending)

    def pending_groups(self):
        return self.election.pending_groups()

    def review_group(self, group_id, approve):
        try:
            group = self.election.review_group(group_id, approve)
        except RuleViolation as exc:
            return Result.failure(str(exc))
        message = "Group %s decided as %s (%d ballots)" % (group.id, group.decision.value, group.size)
        return Result.success(message, group)
