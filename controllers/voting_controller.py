from models.errors import RuleViolation

from .result import Result


class VotingController:
    # handle voter menu

    def __init__(self, election):
        self.election = election

    def candidates(self):
        return self.election.candidates

    def voters(self):
        return self.election.voters

    def voting_is_open(self):
        return self.election.status.name == "OPEN"

    def cast_ballot(self, voter_id, ranking):
        try:
            ballot = self.election.cast_ballot(voter_id, ranking)
        except RuleViolation as exc:
            return Result.failure(str(exc))
        return Result.success("Ballot %s accepted" % ballot.id, ballot)
