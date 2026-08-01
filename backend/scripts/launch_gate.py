"""Avalia evidências JSON de produção, piloto ou lançamento."""

from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path

from ultrastats_ai.release import (
    PilotEvidence,
    ProductionEvidence,
    PublicLaunchEvidence,
    evaluate_pilot,
    evaluate_production,
    evaluate_public_launch,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", choices=("production", "pilot", "public-launch"))
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    if args.gate == "production":
        decision = evaluate_production(ProductionEvidence(**payload))
    elif args.gate == "pilot":
        payload["availability"] = Decimal(str(payload["availability"]))
        payload["feedback_score"] = Decimal(str(payload["feedback_score"]))
        decision = evaluate_pilot(PilotEvidence(**payload))
    else:
        decision = evaluate_public_launch(PublicLaunchEvidence(**payload))
    print(json.dumps({"approved": decision.approved, "blockers": decision.blockers}))
    return 0 if decision.approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
