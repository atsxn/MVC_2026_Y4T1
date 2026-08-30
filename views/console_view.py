from models.election import ElectionStatus

LINE = "-" * 67


class ConsoleView:
    """Console rendering and prompts. No election rule lives in here."""

    def header(self, title, status):
        print("\n" + LINE)
        print("%s  [%s]" % (title, status.value))
        print(LINE)

    def message(self, text):
        print(text)

    def success(self, text):
        print("[OK] " + text)

    def error(self, text):
        print("[REJECTED] " + text)

    # --- menu

    def main_menu(self):
        print("\n1) Voter mode")
        print("2) Officer mode")
        print("3) Status and results")
        print("0) Quit")
        return input("Select: ").strip()

    def voter_menu(self):
        print("\n1) Show candidates")
        print("2) Cast a ranked ballot")
        print("0) Back")
        return input("Select: ").strip()

    def officer_menu(self):
        print("\n1) Close voting")
        print("2) Review flagged pattern groups")
        print("3) Show all ballots")
        print("0) Back")
        return input("Select: ").strip()

    # --- voter side
    def show_candidates(self, candidates):
        print("\nCandidates")
        for candidate in candidates:
            print("  %s  %s" % (candidate.id, candidate.name))

    def show_voters(self, voters):
        print("\nVoters")
        for voter in voters:
            mark = "voted" if voter.has_voted else "not voted"
            suffix = "" if voter.active else "  (inactive)"
            print("  %s  %-16s %-9s%s" % (voter.id, voter.name, mark, suffix))

    def ask_voter_id(self):
        return input("\nVoter id (e.g. V04, blank to cancel): ").strip().upper()

    def ask_ranking(self):
        """Collect three candidate ids. Whatever is typed goes to the model to be judged."""
        ranking = []
        for position in (1, 2, 3):
            value = input("Rank %d (candidate id): " % position).strip().upper()
            if not value:
                return None
            ranking.append(value)
        return ranking

    # --- officer side

    def show_groups(self, groups, pattern_text):
        if not groups:
            print("\nNo repeated pattern group")
            return
        print("\nRepeated pattern groups")
        for group in groups:
            print("  %s  %-18s %d ballots  %s"
                  % (group.id, pattern_text(group.pattern), group.size, group.decision.value))
            print("       ballots: %s" % ", ".join(group.ballot_ids))

    def ask_group_id(self):
        return input("\nGroup id to decide (blank to cancel): ").strip().upper()

    def ask_group_decision(self):
        print("1) Approve  - count every ballot in the group")
        print("2) Reject   - leave every ballot in the group out of the tally")
        return input("Select: ").strip()

    def show_audit(self, rows, pattern_text):
        print("\nAll ballots")
        print("  %-6s %-7s %-18s %-14s %s" % ("BALLOT", "VOTER", "RANKING", "STATUS", "GROUP"))
        for row in rows:
            print("  %-6s %-7s %-18s %-14s %s"
                  % (row["ballot_id"], row["voter_id"], pattern_text(row["ranking"]),
                     row["status"].value, row["group_id"]))

    # --- status and results

    def show_status(self, snapshot, pattern_text):
        status = snapshot["status"]
        print("\nElection status: %s" % status.value)
        print("Ballots accepted: %d" % snapshot["accepted"])

        if status is ElectionStatus.OPEN:
            return

        self.show_groups(snapshot["groups"], pattern_text)
        if status is ElectionStatus.CLOSED:
            print("\nTemporary result (%d certified ballots counted)" % snapshot["certified"])
        else:
            print("\nFinal score (%d certified / %d not counted)"
                  % (snapshot["certified"], snapshot["rejected"]))
        self.show_scores(snapshot)

    def show_scores(self, snapshot):
        scores = snapshot["scores"]
        for candidate in sorted(snapshot["candidates"], key=lambda c: -scores[c.id]):
            print("  %s  %-22s %2d points" % (candidate.id, candidate.name, scores[candidate.id]))
