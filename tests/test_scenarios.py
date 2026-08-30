import unittest

from models.election import ElectionStatus
from models.errors import RuleViolation
from models.repository import load_election


class ExamScenario(unittest.TestCase):
    """T1-T6 run in order against one election exactly like the exam sheet describes."""

    @classmethod
    def setUpClass(cls):
        cls.election = load_election()
    # (Sorry for long names, but they make it easier to follow the exam sheet. (I guess XD))
    def test_t1_v04_casts_a_ballot(self):
        ballot = self.election.cast_ballot("V04", ["C01", "C02", "C03"])
        self.assertEqual(ballot.voter_id, "V04")
        self.assertTrue(self.election.find_voter("V04").has_voted)

    def test_t2_v04_cannot_vote_twice(self):
        with self.assertRaises(RuleViolation):
            self.election.cast_ballot("V04", ["C04", "C05", "C01"])
        self.assertEqual(len(self.election.ballots), 4)

    def test_t2b_incomplete_ranking_is_rejected(self):
        with self.assertRaises(RuleViolation) as ctx:
            self.election.cast_ballot("V05", ["C01", "C02"])
        self.assertIn("exactly 3 candidates", str(ctx.exception))
        self.assertFalse(self.election.find_voter("V05").has_voted)

    def test_t3_duplicate_candidate_is_rejected(self):
        with self.assertRaises(RuleViolation):
            self.election.cast_ballot("V05", ["C04", "C04", "C02"])
        # a rejected ballot must not burn the right to vote
        self.assertFalse(self.election.find_voter("V05").has_voted)

    def test_t4_v05_votes_successfully(self):
        ballot = self.election.cast_ballot("V05", ["C04", "C05", "C01"])
        self.assertEqual(ballot.id, "B05")
        self.assertTrue(self.election.find_voter("V05").has_voted)

    def test_t5_closing_flags_the_repeated_pattern(self):
        pending = self.election.close_voting()
        self.assertEqual(self.election.status, ElectionStatus.CLOSED)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].pattern, ("C01", "C02", "C03"))
        self.assertEqual(pending[0].size, 3)
        # only B03 and B05 count towards the temporary result
        self.assertEqual({b.id for b in self.election.counted_ballots()}, {"B03", "B05"})
        with self.assertRaises(RuleViolation):
            self.election.cast_ballot("V06", ["C01", "C03", "C05"])

    def test_t6_approving_the_group_finalizes_the_election(self):
        group = self.election.pending_groups()[0]
        self.election.review_group(group.id, approve=True)
        self.assertEqual(self.election.status, ElectionStatus.FINALIZED)
        self.assertEqual(self.election.scores(),
                         {"C01": 10, "C02": 9, "C03": 5, "C04": 4, "C05": 2})
        with self.assertRaises(RuleViolation):
            self.election.review_group(group.id, approve=False)


if __name__ == "__main__":
    unittest.main()
