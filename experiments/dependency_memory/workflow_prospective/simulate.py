"""Run a scripted interface control or strictly replay a saved response bundle."""
import argparse
import hashlib
import json
from pathlib import Path

from experiments.dependency_memory.workflow_intake.packet import load_episode, HERE as INTAKE
from . import actor
from .audit import FixtureClient
from .freeze import ROOT, validate_lock
from .runtime import execute


class ReplayClient:
    mode = "saved_response_replay"

    def __init__(self, bundle):
        if bundle["version"] != actor.VERSION or bundle["mode"] != self.mode:
            raise ValueError("Unknown saved-response bundle")
        self.calls = bundle["calls"]
        self.position = 0

    def complete(self, identity, request):
        row = self.calls[self.position]
        if row["identity"] != identity or row["request_sha256"] != hashlib.sha256(actor.request_bytes(request)).hexdigest():
            raise ValueError("Saved response belongs to a different request")
        self.position += 1
        return row["response_text"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", default="E0001")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--fixture", action="store_true")
    modes.add_argument("--responses", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    validate_lock()
    ledger = json.loads((INTAKE / "ledger.json").read_text(encoding="utf-8"))
    if args.episode not in {row["id"] for row in ledger["episodes"] if row["status"] == "complete" and row["split"] == "development"}:
        raise ValueError("This CLI uses registered development evidence only")
    target = args.output.resolve()
    if not target.is_relative_to((ROOT / "build").resolve()) or target.exists():
        raise ValueError("Use a new output file within ignored build/")
    episode = load_episode(INTAKE / "development" / args.episode)
    client = FixtureClient() if args.fixture else ReplayClient(json.loads(args.responses.read_text(encoding="utf-8")))
    trace = execute(episode, client)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as output:
        output.write(actor.wire(trace) + b"\n")
    print(json.dumps({"status": trace["status"], "mode": trace["mode"], "episode": args.episode,
                      "completions": trace["simulated_or_replayed_completions"], "provider_generations": 0,
                      "output": str(target)}, indent=2))


if __name__ == "__main__":
    main()
