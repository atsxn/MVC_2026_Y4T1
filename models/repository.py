import json
from pathlib import Path

from .candidate import Candidate
from .election import Election, ElectionStatus
from .voter import Voter

DEFAULT_SEED = Path(__file__).resolve().parent.parent / "seed_data.json"


def load_election(seed_path=DEFAULT_SEED):
    # load initial data from json file
    with open(seed_path, encoding="utf-8") as handle:
        data = json.load(handle)

    meta = data["election"]
    election = Election(
        election_id=meta["id"],
        title=meta["title"],
        candidates=[Candidate(row["id"], row["name"]) for row in data["candidates"]],
        voters=[Voter(row["id"], row["name"], row.get("active", True)) for row in data["voters"]],
        ranking_points=meta["ranking_points"],
        duplicate_threshold=meta["duplicate_pattern_threshold"],
    )

    for row in data.get("ballots", []):
        election.load_recorded_ballot(row["id"], row["voter_id"], row["ranking"])

    election.status = ElectionStatus[meta["status"]]
    return election
