from enum import Enum

from .ballot import Ballot, BallotStatus
from .errors import RuleViolation
from .pattern_group import GroupDecision, PatternGroup
from .tally import score_ballots

RANKS_REQUIRED = 3


class ElectionStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    FINALIZED = "Finalized"


class Election:
    # store election state and rules
    # other classes should not modify state directly

    def __init__(self, election_id, title, candidates, voters, ranking_points, duplicate_threshold):
        self.id = election_id
        self.title = title
        self.status = ElectionStatus.OPEN
        self.ranking_points = list(ranking_points)
        self.duplicate_threshold = duplicate_threshold
        self.candidates = list(candidates)
        self.voters = list(voters)
        self._candidate_index = {c.id: c for c in self.candidates}
        self._voter_index = {v.id: v for v in self.voters}
        self._ballots = []
        self._groups = []
        self._ballot_seq = 0
        self._group_seq = 0

    # --- lookups

    def find_candidate(self, candidate_id):
        candidate = self._candidate_index.get(candidate_id)
        if candidate is None:
            raise RuleViolation("Unknown candidate id %s" % candidate_id)
        return candidate

    def find_voter(self, voter_id):
        voter = self._voter_index.get(voter_id)
        if voter is None:
            raise RuleViolation("Unknown voter id %s" % voter_id)
        return voter

    def find_group(self, group_id):
        for group in self._groups:
            if group.id == group_id:
                return group
        raise RuleViolation("Unknown pattern group id %s" % group_id)

    def candidate_name(self, candidate_id):
        candidate = self._candidate_index.get(candidate_id)
        return candidate.name if candidate else candidate_id

    # --- voting

    def cast_ballot(self, voter_id, ranking):
        if self.status is not ElectionStatus.OPEN:
            raise RuleViolation("Election is %s, no new ballot is accepted" % self.status.value)
        voter = self.find_voter(voter_id)
        if not voter.active:
            raise RuleViolation("Voter %s is not active and cannot vote" % voter.id)
        if voter.has_voted:
            raise RuleViolation("Voter %s has already voted" % voter.id)
        self._validate_ranking(ranking)

        # mark voter as voted only if all checks pass
        ballot = Ballot(self._next_ballot_id(), voter.id, ranking)
        self._ballots.append(ballot)
        voter.has_voted = True
        return ballot

    def load_recorded_ballot(self, ballot_id, voter_id, ranking):
        # load a ballot from seed data
        voter = self.find_voter(voter_id)
        self._validate_ranking(ranking)
        ballot = Ballot(ballot_id, voter.id, ranking)
        self._ballots.append(ballot)
        voter.has_voted = True
        self._ballot_seq = max(self._ballot_seq, _numeric_suffix(ballot_id))
        return ballot

    def _validate_ranking(self, ranking):
        ranking = list(ranking)
        if len(ranking) != RANKS_REQUIRED:
            raise RuleViolation("A ballot must rank exactly %d candidates" % RANKS_REQUIRED)
        if len(set(ranking)) != RANKS_REQUIRED:
            raise RuleViolation("The %d ranked candidates must all be different" % RANKS_REQUIRED)
        for candidate_id in ranking:
            self.find_candidate(candidate_id)

    # --- closing and duplicate detection

    def close_voting(self):
        if self.status is not ElectionStatus.OPEN:
            raise RuleViolation("Voting can only be closed while the election is open")
        self.status = ElectionStatus.CLOSED
        self._group_duplicate_patterns()
        self._finalize_when_all_reviewed()
        return self.pending_groups()

    def _group_duplicate_patterns(self):
        by_pattern = {}
        for ballot in self._ballots:
            by_pattern.setdefault(ballot.pattern, []).append(ballot)

        for pattern, ballots in by_pattern.items():
            if len(ballots) >= self.duplicate_threshold:
                group = PatternGroup(self._next_group_id(), pattern, [b.id for b in ballots])
                self._groups.append(group)
                for ballot in ballots:
                    ballot.status = BallotStatus.UNDER_REVIEW
                    ballot.group_id = group.id
            else:
                for ballot in ballots:
                    ballot.status = BallotStatus.CERTIFIED

    # --- officer review

    def review_group(self, group_id, approve):
        if self.status is ElectionStatus.FINALIZED:
            raise RuleViolation("The election is finalized, review decisions can no longer be changed")
        if self.status is not ElectionStatus.CLOSED:
            raise RuleViolation("Pattern groups can only be reviewed after voting is closed")
        group = self.find_group(group_id)
        if not group.is_pending():
            raise RuleViolation("Group %s is not pending review, it was already decided as %s"
                                % (group.id, group.decision.value))

        group.decision = GroupDecision.APPROVED if approve else GroupDecision.REJECTED
        new_status = BallotStatus.CERTIFIED if approve else BallotStatus.REJECTED
        for ballot_id in group.ballot_ids:
            self._ballot(ballot_id).status = new_status

        self._finalize_when_all_reviewed()
        return group

    def _finalize_when_all_reviewed(self):
        if self.status is ElectionStatus.CLOSED and not self.pending_groups():
            self.status = ElectionStatus.FINALIZED

    # --- reporting

    @property
    def ballots(self):
        return list(self._ballots)

    @property
    def groups(self):
        return list(self._groups)

    def pending_groups(self):
        return [group for group in self._groups if group.is_pending()]

    def counted_ballots(self):
        return [ballot for ballot in self._ballots if ballot.is_counted()]

    def rejected_ballots(self):
        return [ballot for ballot in self._ballots if ballot.status is BallotStatus.REJECTED]

    def under_review_ballots(self):
        return [ballot for ballot in self._ballots if ballot.status is BallotStatus.UNDER_REVIEW]

    def scores(self):
        """Points from certified ballots only. Ties are reported as-is, no winner is picked."""
        return score_ballots(self.counted_ballots(), self.candidates, self.ranking_points)

    # --- id generation

    def _ballot(self, ballot_id):
        for ballot in self._ballots:
            if ballot.id == ballot_id:
                return ballot
        raise RuleViolation("Unknown ballot id %s" % ballot_id)

    def _next_ballot_id(self):
        self._ballot_seq += 1
        return "B%02d" % self._ballot_seq

    def _next_group_id(self):
        self._group_seq += 1
        return "G%02d" % self._group_seq


def _numeric_suffix(identifier):
    digits = "".join(ch for ch in identifier if ch.isdigit())
    return int(digits) if digits else 0
