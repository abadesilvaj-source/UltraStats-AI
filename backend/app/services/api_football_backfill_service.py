from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Mapping

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.competition_catalog import (
    competition_is_modeled,
    competition_policy,
    competition_priority,
)
from app.models import Competition
from app.services.match_fusion_service import MatchFusionService
from app.services.operational_pipeline_service import OperationalPipelineService
from ultrastats_ai.infrastructure.database.models import RawProviderPayloadRecord
from ultrastats_ai.infrastructure.providers import (
    DataCapability,
    RawProviderPayload,
    build_multi_source_engine,
)
from ultrastats_ai.infrastructure.providers.persistence import (
    SqlAlchemyRawPayloadStore,
)


class ApiFootballBackfillService:
    """Backfill incremental, reiniciável e limitado por orçamento."""

    def __init__(
        self,
        session: Session,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        self.session = session
        self.environment = os.environ if environment is None else environment
        self.store = SqlAlchemyRawPayloadStore(session)

    def run(
        self,
        *,
        seasons_per_league: int = 3,
        request_budget: int | None = None,
        include_statistics: bool = True,
    ) -> dict[str, Any]:
        budget = request_budget or int(
            self.environment.get("AUTO_BACKFILL_REQUEST_BUDGET", "5000")
        )
        if budget <= 0 or seasons_per_league <= 0:
            raise ValueError("Orçamento e número de temporadas devem ser positivos.")
        engine = build_multi_source_engine(self.environment)
        source = next(
            item for item in engine.sources if item.name == "api_football"
        )
        calls = batches = fixtures_saved = statistics_saved = players_saved = 0
        failures: list[str] = []
        reserve = max(
            0, int(self.environment.get("API_FOOTBALL_MIN_REMAINING", "10000"))
        )

        def quota_available(required: int = 1) -> bool:
            remaining = dict(
                getattr(source, "last_rate_limit", {}) or {}
            ).get("x-ratelimit-requests-remaining")
            try:
                return remaining is None or int(remaining) - required >= reserve
            except (TypeError, ValueError):
                return True
        try:
            coverage = source.collect(DataCapability.COVERAGE, current="true")
            calls += 1
            targets: list[tuple[int, int, int, str]] = []
            for observation in coverage:
                row = observation.values
                league = row.get("league") or {}
                country = row.get("country") or {}
                policy = competition_policy(
                    str(league.get("name") or ""),
                    str(country.get("name") or ""),
                )
                league_id = int(league.get("id") or 0)
                competition = self.session.scalar(
                    select(Competition).where(
                        Competition.source == "api_football",
                        Competition.external_id == str(league_id),
                    )
                ) if league_id else None
                if policy is None and not competition_is_modeled(competition):
                    continue
                seasons = sorted(
                    {
                        int(item.get("year"))
                        for item in (row.get("seasons") or ())
                        if item.get("year") is not None
                        and (
                            (
                                (item.get("coverage") or {})
                                .get("fixtures") or {}
                            ).get("statistics_fixtures")
                            is True
                        )
                    },
                    reverse=True,
                )[:seasons_per_league]
                targets.extend(
                    (
                        competition_priority(policy) if policy else 40,
                        league_id,
                        season,
                        str(league.get("name") or league_id),
                    )
                    for season in seasons
                    if league_id
                )

            for _, league_id, season, league_name in sorted(targets):
                if calls >= budget or not quota_available(1):
                    break
                marker = f"{league_id}:{season}"
                completed_marker = self.session.scalar(
                    select(RawProviderPayloadRecord.payload).where(
                        RawProviderPayloadRecord.provider == "api_football",
                        RawProviderPayloadRecord.resource == "backfill_batch",
                        RawProviderPayloadRecord.external_id == marker,
                    ).order_by(
                        RawProviderPayloadRecord.collected_at.desc()
                    ).limit(1)
                )
                if completed_marker and completed_marker.get(
                    "statistics_complete", False
                ):
                    continue
                try:
                    fixtures = source.collect(
                        DataCapability.FIXTURES,
                        league=league_id,
                        season=season,
                        timezone="America/Sao_Paulo",
                    )
                    calls += 1
                    for item in fixtures:
                        fixtures_saved += self.store.save(
                            RawProviderPayload(
                                "api_football",
                                "fixtures",
                                item.external_id,
                                item.values,
                                item.observed_at,
                            )
                        )
                    MatchFusionService(self.session).fuse(fixtures)
                    OperationalPipelineService(self.session).process(
                        fixtures=fixtures,
                        odds=(),
                    )
                    self.session.flush()

                    statistics_complete = not include_statistics
                    if include_statistics:
                        finished = [
                            item for item in fixtures
                            if str(
                                ((item.values.get("fixture") or {})
                                 .get("status") or {}).get("short") or ""
                            ) in {"FT", "AET", "PEN"}
                        ]
                        processed_finished = 0
                        for fixture in finished:
                            fixture_id = str(
                                (fixture.values.get("fixture") or {}).get("id")
                                or fixture.external_id
                            )
                            existing_statistics = self.session.scalar(
                                select(func.count()).select_from(
                                    RawProviderPayloadRecord
                                ).where(
                                    RawProviderPayloadRecord.provider
                                    == "api_football",
                                    RawProviderPayloadRecord.resource
                                    == "statistics",
                                    RawProviderPayloadRecord.external_id.like(
                                        f"{fixture_id}:%"
                                    ),
                                )
                            ) or 0
                            attempts = self.session.scalars(
                                select(RawProviderPayloadRecord).where(
                                    RawProviderPayloadRecord.provider
                                    == "api_football",
                                    RawProviderPayloadRecord.resource
                                    == "backfill_statistics_attempt",
                                    RawProviderPayloadRecord.external_id
                                    == fixture_id,
                                ).order_by(
                                    RawProviderPayloadRecord.collected_at.desc()
                                )
                            ).all()
                            latest_attempt = attempts[0] if attempts else None
                            latest_status = (
                                str(latest_attempt.payload.get("status") or "")
                                if latest_attempt else ""
                            )
                            retry_hours = max(
                                1,
                                int(self.environment.get(
                                    "BACKFILL_EMPTY_RETRY_HOURS", "24"
                                )),
                            )
                            max_empty_attempts = max(
                                1,
                                int(self.environment.get(
                                    "BACKFILL_MAX_EMPTY_ATTEMPTS", "5"
                                )),
                            )
                            retry_cutoff = (
                                datetime.now(timezone.utc)
                                - timedelta(hours=retry_hours)
                            )
                            waiting_for_retry = bool(
                                latest_attempt
                                and latest_status == "empty"
                                and self._as_aware(
                                    latest_attempt.collected_at
                                ) >= retry_cutoff
                            )
                            exhausted = (
                                latest_status == "empty"
                                and len(attempts) >= max_empty_attempts
                            )
                            if (
                                existing_statistics >= 2
                                or latest_status == "received"
                                or exhausted
                            ):
                                processed_finished += 1
                                continue
                            if waiting_for_retry:
                                continue
                            if calls + 2 > budget or not quota_available(2):
                                break
                            try:
                                statistics = source.collect(
                                    DataCapability.STATISTICS,
                                    fixture=fixture_id,
                                )
                                calls += 1
                                attempted_at = datetime.now(timezone.utc)
                                self.store.save(RawProviderPayload(
                                    "api_football",
                                    "backfill_statistics_attempt",
                                    fixture_id,
                                    {
                                        "fixture_id": fixture_id,
                                        "status": (
                                            "received" if statistics
                                            else "empty"
                                        ),
                                        "attempt": len(attempts) + 1,
                                        "retry_after_hours": (
                                            retry_hours
                                            if not statistics else None
                                        ),
                                    },
                                    attempted_at,
                                ))
                                for item in statistics:
                                    statistics_saved += self.store.save(
                                        RawProviderPayload(
                                            "api_football",
                                            "statistics",
                                            f"{fixture_id}:{item.external_id}",
                                            item.values,
                                            item.observed_at,
                                        )
                                    )
                                result = OperationalPipelineService(
                                    self.session
                                ).process_post_match_statistics(
                                    fixture, statistics
                                )
                                statistics_saved += int(
                                    result.get("statistics", 0)
                                )
                                players = source.collect(
                                    DataCapability.PLAYER_STATISTICS,
                                    fixture=fixture_id,
                                )
                                calls += 1
                                for item in players:
                                    players_saved += self.store.save(
                                        RawProviderPayload(
                                            "api_football",
                                            "player_statistics",
                                            f"{fixture_id}:{item.external_id}",
                                            item.values,
                                            item.observed_at,
                                        )
                                    )
                                processed_finished += 1
                            except Exception as error:
                                failures.append(
                                    f"{fixture_id}:{type(error).__name__}"
                                )
                        statistics_complete = (
                            processed_finished == len(finished)
                        )
                    now = datetime.now(timezone.utc)
                    if statistics_complete:
                        self.store.save(RawProviderPayload(
                            "api_football",
                            "backfill_batch",
                            marker,
                            {
                                "league": league_name,
                                "league_id": league_id,
                                "season": season,
                                "fixtures": len(fixtures),
                                "statistics_complete": True,
                                "completed_at": now.isoformat(),
                            },
                            now,
                        ))
                    self.session.commit()
                    batches += int(statistics_complete)
                except Exception as error:
                    self.session.rollback()
                    failures.append(
                        f"{league_id}:{season}:{type(error).__name__}:{error}"
                    )
            return {
                "request_budget": budget,
                "requests_used": calls,
                "batches_completed": batches,
                "fixtures_saved": fixtures_saved,
                "statistics_saved": statistics_saved,
                "player_statistics_saved": players_saved,
                "failures": failures[:100],
                "resumable": True,
            }
        finally:
            engine.close()

    @staticmethod
    def _as_aware(value: datetime) -> datetime:
        return (
            value.replace(tzinfo=timezone.utc)
            if value.tzinfo is None else value.astimezone(timezone.utc)
        )
