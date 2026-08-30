import sys

from controllers.app_controller import AppController
from models.repository import load_election
from views.console_view import ConsoleView


def main():
    # windows consoles still default to cp874 here, which cannot print the Thai labels
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    election = load_election()
    AppController(election, ConsoleView()).run()


if __name__ == "__main__":
    main()
