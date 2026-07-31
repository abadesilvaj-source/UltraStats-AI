import argparse
import json

from app.database.session import SessionLocal
from app.services.api_football_backfill_service import (
    ApiFootballBackfillService,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill incremental API-Football Ultra."
    )
    parser.add_argument("--seasons", type=int, default=3)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--without-statistics", action="store_true")
    args = parser.parse_args()
    session = SessionLocal()
    try:
        result = ApiFootballBackfillService(session).run(
            seasons_per_league=args.seasons,
            request_budget=args.budget,
            include_statistics=not args.without_statistics,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    main()
