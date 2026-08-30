from .officer_controller import OfficerController
from .report_controller import ReportController
from .voting_controller import VotingController


class AppController:
    # manage main menu and call other controllers

    def __init__(self, election, view):
        self.election = election
        self.view = view
        self.voting = VotingController(election)
        self.officer = OfficerController(election)
        self.report = ReportController(election)

    def run(self):
        while True:
            self.view.header(self.election.title, self.election.status)
            choice = self.view.main_menu()
            if choice == "1":
                self._voter_mode()
            elif choice == "2":
                self._officer_mode()
            elif choice == "3":
                self._show_status()
            elif choice == "0":
                self.view.message("Bye")
                return
            else:
                self.view.error("No such menu option")

    # --- voter

    def _voter_mode(self):
        while True:
            choice = self.view.voter_menu()
            if choice == "1":
                self.view.show_candidates(self.voting.candidates())
            elif choice == "2":
                self._cast_ballot()
            elif choice == "0":
                return
            else:
                self.view.error("No such menu option")

    def _cast_ballot(self):
        self.view.show_voters(self.voting.voters())
        voter_id = self.view.ask_voter_id()
        if not voter_id:
            return
        self.view.show_candidates(self.voting.candidates())
        ranking = self.view.ask_ranking()
        if ranking is None:
            self.view.error("Ballot cancelled. The voter keeps the right to vote")
            return

        result = self.voting.cast_ballot(voter_id, ranking)
        if result.ok:
            self.view.success(result.message)
        else:
            self.view.error(result.message)

    # --- officer

    def _officer_mode(self):
        while True:
            choice = self.view.officer_menu()
            if choice == "1":
                self._close_voting()
            elif choice == "2":
                self._review_group()
            elif choice == "3":
                self.view.show_audit(self.report.audit_rows(), self.report.pattern_text)
            elif choice == "0":
                return
            else:
                self.view.error("No such menu option")

    def _close_voting(self):
        result = self.officer.close_voting()
        if not result.ok:
            self.view.error(result.message)
            return
        self.view.success(result.message)
        self._show_status()

    def _review_group(self):
        self.view.show_groups(self.election.groups, self.report.pattern_text)
        group_id = self.view.ask_group_id()
        if not group_id:
            return
        choice = self.view.ask_group_decision()
        if choice not in ("1", "2"):
            self.view.error("A group can only be approved or not counted")
            return

        result = self.officer.review_group(group_id, approve=(choice == "1"))
        if result.ok:
            self.view.success(result.message)
            self._show_status()
        else:
            self.view.error(result.message)

    # --- status

    def _show_status(self):
        self.view.show_status(self.report.snapshot(), self.report.pattern_text)
