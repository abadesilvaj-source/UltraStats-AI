from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo
import os

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app.models import Audit, Bet, Competition, Match, MatchStatistics, Prediction
from app.services.sync_monitor_service import SyncMonitorService
from ultrastats_ai.infrastructure.providers import (
    DataCapability,
    MultiSourceEngine,
    RawProviderPayload,
    SourceObservation,
    build_football_data_provider,
    build_multi_source_engine,
)
from ultrastats_ai.infrastructure.providers.persistence import (
    SqlAlchemyHealthStore,
    SqlAlchemyRawPayloadStore,
)
from ultrastats_ai.infrastructure.database.models import (
    IdentityDecisionRecord,
    LiveEventRecord,
    RawProviderPayloadRecord,
)
from app.services.operational_pipeline_service import OperationalPipelineService
from app.services.match_fusion_service import MatchFusionService
from app.services.historical_enrichment_service import HistoricalEnrichmentService
from app.services.operational_intelligence_service import (
    OperationalIntelligenceService,
)
from app.services.maturity_service import MaturityService
from app.services.post_match_service import PostMatchService
from app.services.learning_pipeline_service import LearningPipelineService
from app.services.api_football_backfill_service import (
    ApiFootballBackfillService,
)
from app.services.closing_odds_service import ClosingOddsService
from app.core.competition_catalog import (
    competition_is_modeled,
    competition_policy,
    competition_priority,
)
from ultrastats_ai.domain.live import (
    LiveEngine,
    LiveEvent,
    LiveEventType,
    LiveHealth,
    LiveMatchState,
    LivePhase,
    LiveRecommendation,
)
from ultrastats_ai.infrastructure.live import LiveStore


class MultiProviderSyncService:
    """Executa e audita a coleta periódica das fontes reais."""

    def __init__(
        self,
        session: Session,
        *,
        environment: Mapping[str, str] | None = None,
        engine_factory: Callable[[Mapping[str, str]], MultiSourceEngine] = (
            build_multi_source_engine
        ),
        football_factory: Callable[[], object] = build_football_data_provider,
    ) -> None:
        self.session = session
        self.environment = os.environ if environment is None else environment
        self.engine_factory = engine_factory
        self.football_factory = football_factory
        self.monitor = SyncMonitorService(session)
        self.raw_store = SqlAlchemyRawPayloadStore(session)
        self.health_store = SqlAlchemyHealthStore(session)

    def run(self, *, triggered_by: str = "scheduler") -> dict[str, object]:
        sync_run = self.monitor.start_run("multi_provider", triggered_by)
        engine = self.engine_factory(self.environment)
        football_provider = None
        football_data_payload = None
        saved = 0
        skipped = 0
        failures: dict[str, str] = {}

        try:
            for source in engine.sources:
                health = source.health_check()
                self.health_store.save(health)
                if not health.available:
                    failures[source.name] = health.message

            parameters = self._fixture_parameters()
            report = engine.collect(
                DataCapability.FIXTURES,
                source_params={
                    "api_football": {
                        "date": parameters["date"],
                        "timezone": "America/Sao_Paulo",
                    },
                    "openligadb": {
                        "league": parameters["league"],
                        "season": parameters["season"],
                    },
                    "football_data_uk": {
                        "path": parameters["path"],
                    },
                    "thesportsdb": {
                        "date": parameters["date"],
                    },
                    "sportmonks": {
                        "date": parameters["date"],
                    },
                    "goal_api": {
                        "date": parameters["date"],
                        "limit": 100,
                    },
                    "zafronix": {
                        "year": int(parameters["season"][:4]),
                        "limit": 200,
                    },
                },
            )
            failures.update(report.failed_sources)
            for observation in report.observations:
                payload = RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
                if self.raw_store.save(payload):
                    saved += 1
                else:
                    skipped += 1

            odds_report = engine.collect(
                DataCapability.ODDS,
                source_params={
                    "api_football": {
                        "date": parameters["date"],
                    },
                    "the_odds_api": {
                        "sport_keys": tuple(
                            key.strip()
                            for key in self.environment.get(
                                "THE_ODDS_API_SPORT_KEYS",
                                "soccer_brazil_campeonato,"
                                "soccer_brazil_serie_b,"
                                "soccer_conmebol_copa_libertadores,"
                                "soccer_conmebol_copa_sudamericana,"
                                "soccer_epl,soccer_spain_la_liga,"
                                "soccer_germany_bundesliga,"
                                "soccer_italy_serie_a,"
                                "soccer_france_ligue_one,"
                                "soccer_portugal_primeira_liga,"
                                "soccer_netherlands_eredivisie,"
                                "soccer_uefa_champs_league,"
                                "soccer_uefa_europa_league,"
                                "fifa_world_cup",
                            ).split(",")
                            if key.strip()
                        ),
                        "regions": self.environment.get(
                            "THE_ODDS_API_REGIONS", "eu"
                        ),
                        "markets": self.environment.get(
                            "THE_ODDS_API_MARKETS", "h2h,totals"
                        ),
                    },
                },
            )
            failures.update(odds_report.failed_sources)
            for observation in odds_report.observations:
                payload = RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
                if self.raw_store.save(payload):
                    saved += 1
                else:
                    skipped += 1
            separate_odds_worker = self.environment.get(
                "ODDS_SYNC_ENABLED", "true"
            ).strip().casefold() in {"true", "1", "yes", "on"}
            targeted_odds = (
                () if separate_odds_worker
                else self._collect_targeted_api_football_odds(
                    engine, report.observations
                )
            )
            for observation in targeted_odds:
                if self.raw_store.save(RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )):
                    saved += 1
                else:
                    skipped += 1
            all_odds = odds_report.observations + targeted_odds

            active_providers = {
                name.strip()
                for name in self.environment.get(
                    "ACTIVE_PROVIDERS", ""
                ).split(",")
                if name.strip()
            }
            if (
                self.environment.get("FOOTBALL_DATA_API_TOKEN", "").strip()
                and (
                    not active_providers
                    or "football_data" in active_providers
                )
            ):
                football_provider = self.football_factory()
                health = football_provider.health_check()
                self.health_store.save(health)
                if health.available:
                    data = football_provider.fetch_matches(
                        dateFrom=parameters["date"],
                        dateTo=parameters["date"],
                    )
                    football_data_payload = data
                    payload = RawProviderPayload(
                        "football_data",
                        "matches",
                        parameters["date"],
                        data,
                        datetime.now(timezone.utc),
                    )
                    if self.raw_store.save(payload):
                        saved += 1
                    else:
                        skipped += 1
                else:
                    failures["football_data"] = health.message

            if not report.successful_sources and (
                football_provider is None
                or failures.get("football_data") is not None
            ):
                raise RuntimeError("Nenhum provider real respondeu com sucesso.")

            # A coleta bruta é o ativo primário. Ela deve sobreviver mesmo se
            # um estágio derivado (previsão, ML ou recomendações) degradar.
            self.session.commit()

            lineups_saved = self._run_stage(
                "lineups",
                lambda: self._collect_lineups(
                    engine, report.observations
                ),
                failures,
                0,
            )
            enrichment = self._run_stage(
                "api_football_ultra_enrichment",
                lambda: self._collect_api_football_enrichment(
                    engine, report.observations
                ),
                failures,
                {},
            )
            fusion_observations = (
                report.observations + all_odds
            )
            fusion_result = self._run_stage(
                "fusion",
                lambda: MatchFusionService(self.session).fuse(
                    fusion_observations,
                    football_data_payload=football_data_payload,
                ),
                failures,
                {},
            )
            operational = self._run_stage(
                "operational_pipeline",
                lambda: OperationalPipelineService(self.session).process(
                    fixtures=report.observations,
                    odds=all_odds,
                ),
                failures,
                {},
            )
            operational["fusion"] = fusion_result
            operational["historical_enrichment"] = self._run_stage(
                "historical_enrichment",
                lambda: HistoricalEnrichmentService(
                    self.session
                ).process(report.observations),
                failures,
                {},
            )
            if (
                self.environment.get("API_FOOTBALL_KEY", "").strip()
                and self.environment.get(
                    "BACKFILL_SEPARATE_WORKER", "true"
                ).strip().casefold() not in {"true", "1", "yes", "on"}
            ):
                # O backfill possui checkpoints/commits próprios para ser
                # reiniciável. Executá-lo dentro de begin_nested() fecha o
                # savepoint prematuramente e invalida a transação externa.
                self.session.commit()
                try:
                    operational["api_football_backfill"] = (
                        ApiFootballBackfillService(
                            self.session, self.environment
                        ).run(
                        seasons_per_league=max(
                            1,
                            int(self.environment.get(
                                "AUTO_BACKFILL_SEASONS", "3"
                            )),
                        ),
                        request_budget=max(
                            1,
                            int(self.environment.get(
                                "AUTO_BACKFILL_REQUESTS_PER_SYNC", "250"
                            )),
                        ),
                        include_statistics=True,
                        )
                    )
                except Exception as error:
                    self.session.rollback()
                    failures["stage:api_football_backfill"] = (
                        f"{type(error).__name__}: {error}"
                    )
                    operational["api_football_backfill"] = {}
            else:
                operational["api_football_backfill"] = {
                    "status": "separate_worker"
                }
            operational["fusion_predictions"] = self._run_stage(
                "fusion_predictions",
                lambda: OperationalPipelineService(
                    self.session
                ).refresh_all_predictions(),
                failures,
                0,
            )
            operational["live_snapshots"] = self._run_stage(
                "live_snapshots",
                lambda: self._persist_live_snapshots(
                    report.observations
                ),
                failures,
                0,
            )
            operational["lineups"] = lineups_saved
            operational["api_football_enrichment"] = enrichment
            statistics_saved, settled_bets = self._run_stage(
                "post_match_statistics",
                lambda: self._collect_post_match_statistics(
                    engine,
                    report.observations,
                    unavailable_sources=frozenset(failures),
                ),
                failures,
                (0, 0),
            )
            operational["statistics"] = statistics_saved
            operational["settled_bets"] = settled_bets
            operational["score_learning"] = self._run_stage(
                "score_learning",
                self._learn_from_finished_scores,
                failures,
                {
                    "matches_processed": 0,
                    "predictions_audited": 0,
                },
            )
            operational["post_match_predictions"] = self._run_stage(
                "post_match_predictions",
                lambda: OperationalPipelineService(
                    self.session
                ).refresh_all_predictions(),
                failures,
                0,
            )
            operational["closing_odds_marked"] = self._run_stage(
                "closing_odds",
                lambda: ClosingOddsService(self.session).mark(),
                failures,
                0,
            )
            operational["intelligence"] = self._run_stage(
                "intelligence",
                lambda: OperationalIntelligenceService(
                    self.session
                ).run(),
                failures,
                {},
            )
            operational["maturity"] = self._run_stage(
                "maturity",
                lambda: MaturityService(self.session).run(),
                failures,
                {},
            )
            operational["stale_matches_reconciled"] = self._run_stage(
                "stale_reconciliation",
                self._reconcile_stale_matches,
                failures,
                0,
            )
            self.session.commit()
            completed = self.monitor.mark_success(
                sync_run.id,
                {
                    "matches": {
                        "created": saved,
                        "updated": 0,
                        "skipped": skipped,
                    },
                    "warnings": failures,
                },
            )
            return {
                "sync_run_id": completed.id,
                "status": completed.status,
                "duration_seconds": completed.duration_seconds,
                "saved": saved,
                "skipped": skipped,
                "successful_sources": report.successful_sources,
                "failures": failures,
                "degraded": bool(failures),
                "operational": operational,
            }
        except Exception as error:
            self.session.rollback()
            self.monitor.mark_failed(sync_run.id, error)
            raise
        finally:
            engine.close()
            if football_provider is not None:
                football_provider.close()

    def run_live(
        self, *, triggered_by: str = "scheduler"
    ) -> dict[str, object]:
        """Atualiza somente placares ao vivo, preservando as cotas gratuitas."""
        sync_run = self.monitor.start_run(
            "multi_provider_live", triggered_by
        )
        engine = self.engine_factory(self.environment)
        saved = skipped = 0
        failures: dict[str, str] = {}
        try:
            report = engine.collect(
                DataCapability.LIVE,
                source_params={
                    "api_football": {
                        "live": "all",
                        "timezone": "America/Sao_Paulo",
                    },
                    "sportmonks": {},
                },
            )
            failures.update(report.failed_sources)
            if not report.successful_sources:
                raise RuntimeError(
                    "Nenhum provider de placar ao vivo respondeu."
                )
            for observation in report.observations:
                if self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=observation.external_id,
                        payload=observation.values,
                        collected_at=observation.observed_at,
                    )
                ):
                    saved += 1
                else:
                    skipped += 1

            live_details = self._run_stage(
                "live_details",
                lambda: self._collect_live_details(
                    engine, report.observations
                ),
                failures,
                {},
            )

            fusion = self._run_stage(
                "live_fusion",
                lambda: MatchFusionService(self.session).fuse(
                    report.observations
                ),
                failures,
                {},
            )
            snapshots = self._run_stage(
                "live_snapshots",
                lambda: self._persist_live_snapshots(
                    report.observations
                ),
                failures,
                0,
            )
            reconciled = self._run_stage(
                "stale_reconciliation",
                lambda: self._reconcile_stale_matches(
                    report.observations
                ),
                failures,
                0,
            )
            closing_odds = self._run_stage(
                "closing_odds",
                lambda: ClosingOddsService(self.session).mark(),
                failures,
                0,
            )
            self.session.commit()
            completed = self.monitor.mark_success(
                sync_run.id,
                {
                    "matches": {
                        "created": saved,
                        "updated": 0,
                        "skipped": skipped,
                    },
                    "warnings": failures,
                },
            )
            return {
                "sync_run_id": completed.id,
                "status": completed.status,
                "duration_seconds": completed.duration_seconds,
                "saved": saved,
                "skipped": skipped,
                "successful_sources": report.successful_sources,
                "failures": failures,
                "degraded": bool(failures),
                "operational": {
                    "fusion": fusion,
                    "live_snapshots": snapshots,
                    "live_details": live_details,
                    "closing_odds_marked": closing_odds,
                    "stale_matches_reconciled": reconciled,
                },
            }
        except Exception as error:
            self.session.rollback()
            self.monitor.mark_failed(sync_run.id, error)
            raise
        finally:
            engine.close()

    def run_backfill(self, *, triggered_by: str = "scheduler") -> dict[str, object]:
        """Executa o preenchimento histórico sem prender o ciclo esportivo."""
        sync_run = self.monitor.start_run("api_football_backfill", triggered_by)
        engine = self.engine_factory(self.environment)
        try:
            targeted_statistics, settled_bets = self._collect_post_match_statistics(
                engine, (), unavailable_sources=frozenset()
            )
            self.session.commit()
            historical_budget = max(0, int(self.environment.get(
                "AUTO_HISTORICAL_BACKFILL_PER_CYCLE", "50"
            )))
            result = {
                "request_budget": historical_budget, "requests_used": 0,
                "batches_completed": 0, "fixtures_saved": 0,
                "statistics_saved": 0, "player_statistics_saved": 0,
                "failures": [], "resumable": True,
            }
            if historical_budget:
                result = ApiFootballBackfillService(
                    self.session, self.environment
                ).run(
                    seasons_per_league=max(
                        1, int(self.environment.get("AUTO_BACKFILL_SEASONS", "3"))
                    ),
                    request_budget=historical_budget,
                    include_statistics=True,
                )
            result["targeted_statistics_saved"] = targeted_statistics
            result["settled_bets"] = settled_bets
            completed = self.monitor.mark_success(
                sync_run.id,
                {"matches": {"created": (
                    result["statistics_saved"] + targeted_statistics
                ), "updated": 0,
                             "skipped": 0}, "warnings": result.get("failures", ())},
            )
            return {"sync_run_id": completed.id, "status": completed.status, **result}
        except Exception as error:
            self.session.rollback()
            self.monitor.mark_failed(sync_run.id, error)
            raise
        finally:
            engine.close()

    def run_odds_refresh(
        self, *, triggered_by: str = "scheduler"
    ) -> dict[str, object]:
        """Atualiza odds em janela móvel, promovendo-as e recalculando previsões."""
        sync_run = self.monitor.start_run("multi_provider_odds", triggered_by)
        engine = self.engine_factory(self.environment)
        saved = skipped = 0
        failures: dict[str, str] = {}
        try:
            api_source = next(
                (source for source in engine.sources if source.name == "api_football"),
                None,
            )
            days = max(1, int(self.environment.get("ODDS_SYNC_WINDOW_DAYS", "14")))
            # O ciclo frequente prioriza jogos iminentes. Tentar toda a janela
            # em uma execução pode exceder o intervalo do scheduler quando um
            # provedor está lento e deixa a série inteira obsoleta.
            days_per_cycle = min(
                days,
                max(1, int(self.environment.get(
                    "ODDS_SYNC_DAYS_PER_CYCLE", "3"
                ))),
            )
            fixture_observations: list[SourceObservation] = []
            odds_observations: list[SourceObservation] = []
            if api_source is not None:
                consecutive_failures = 0
                # Hoje é sempre prioritário. Os demais dias giram entre ciclos
                # para cobrir toda a janela sem multiplicar o consumo de cota.
                interval_seconds = max(
                    60,
                    int(self.environment.get(
                        "ODDS_SYNC_INTERVAL_MINUTES", "15"
                    )) * 60,
                )
                slot = int(datetime.now(timezone.utc).timestamp()) // interval_seconds
                future_offsets: list[int] = []
                if days > 0:
                    start = 1 + ((slot * days_per_cycle) % days)
                    future_offsets = [
                        1 + ((start - 1 + index) % days)
                        for index in range(days_per_cycle)
                    ]
                for offset in [0, *future_offsets]:
                    target = (datetime.now(ZoneInfo("America/Sao_Paulo"))
                              + timedelta(days=offset)).date().isoformat()
                    if not self._quota_allows(api_source):
                        break
                    try:
                        fixtures = api_source.collect(
                            DataCapability.FIXTURES,
                            date=target,
                            timezone="America/Sao_Paulo",
                        )
                        fixture_observations.extend(fixtures)
                        odds_observations.extend(api_source.collect(
                            DataCapability.ODDS, date=target
                        ))
                        consecutive_failures = 0
                    except Exception as error:
                        failures[f"api_football:{target}"] = str(error)
                        consecutive_failures += 1
                        if consecutive_failures >= 2:
                            failures["api_football:circuit_breaker"] = (
                                "Coleta interrompida após duas falhas consecutivas."
                            )
                            break

            odds_source = next(
                (source for source in engine.sources if source.name == "the_odds_api"),
                None,
            )
            if odds_source is not None:
                try:
                    odds_observations.extend(odds_source.collect(
                        DataCapability.ODDS,
                        sport_keys=self._rotating_odds_sport_keys(),
                        regions=self.environment.get("THE_ODDS_API_REGIONS", "eu"),
                        markets=self.environment.get("THE_ODDS_API_MARKETS", "h2h,totals"),
                    ))
                except Exception as error:
                    failures["the_odds_api"] = str(error)

            # Uma coleta pode ser interrompida depois de salvar a agenda e
            # antes da fusão. Recuperar a camada bruta impede que partidas
            # válidas desapareçam de "Em breve" e "Próximas partidas".
            fixture_keys = {
                (item.provider, item.external_id)
                for item in fixture_observations
            }
            recovered_fixtures: list[SourceObservation] = []
            for recovered in self._recent_raw_fixtures(hours=36):
                key = (recovered.provider, recovered.external_id)
                if key not in fixture_keys:
                    recovered_fixtures.append(recovered)
                    fixture_keys.add(key)

            recovered_schedule = OperationalPipelineService(
                self.session
            ).promote_fixtures_only(tuple(recovered_fixtures))
            self.session.flush()

            # Recupera payloads recentes que sobreviveram a uma interrupção
            # entre a coleta e a promoção. Isso é idempotente e evita gastar
            # novamente as cotas dos provedores gratuitos.
            observed_keys = {
                (item.provider, item.external_id, item.observed_at)
                for item in odds_observations
            }
            for recovered in self._recent_raw_odds(hours=12):
                key = (
                    recovered.provider,
                    recovered.external_id,
                    recovered.observed_at,
                )
                if key not in observed_keys:
                    odds_observations.append(recovered)
                    observed_keys.add(key)

            for observation in (*fixture_observations, *odds_observations):
                created = self.raw_store.save(RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                ))
                saved += int(created)
                skipped += int(not created)
            self.session.commit()
            fused = MatchFusionService(self.session).fuse(tuple(fixture_observations))
            promoted = OperationalPipelineService(
                self.session, temporal_ml_training=False
            ).process(
                fixtures=tuple(fixture_observations),
                odds=tuple(odds_observations),
                predict_only_with_odds=True,
            )
            closing_marked = ClosingOddsService(self.session).mark()
            # ``process`` já recalcula as partidas presentes na janela. Um
            # refresh global aqui reprocessaria centenas de milhares de linhas
            # em todo ciclo e atrasaria desnecessariamente a disponibilidade.
            refreshed = int(promoted.get("predictions", 0))
            self._persist_quota_snapshot(api_source) if api_source else None
            self.session.commit()
            completed = self.monitor.mark_success(
                sync_run.id,
                {"matches": {"created": saved, "updated": 0, "skipped": skipped},
                 "warnings": failures},
            )
            return {
                "sync_run_id": completed.id,
                "status": completed.status,
                "fixtures": len(fixture_observations),
                "odds": len(odds_observations),
                "saved": saved,
                "skipped": skipped,
                "fusion": fused,
                "promoted": promoted,
                "recovered_schedule": recovered_schedule,
                "predictions_refreshed": refreshed,
                "closing_odds_marked": closing_marked,
                "failures": failures,
            }
        except Exception as error:
            self.session.rollback()
            self.monitor.mark_failed(sync_run.id, error)
            raise
        finally:
            engine.close()

    def _rotating_odds_sport_keys(self) -> tuple[str, ...]:
        """Distribui ligas entre ciclos sem monopolizar o worker ao vivo."""
        keys = tuple(
            key.strip()
            for key in self.environment.get(
                "THE_ODDS_API_SPORT_KEYS",
                "soccer_brazil_campeonato",
            ).split(",")
            if key.strip()
        )
        if not keys:
            return ("upcoming",)
        batch_size = min(
            len(keys),
            max(1, int(self.environment.get(
                "THE_ODDS_API_KEYS_PER_CYCLE", "4"
            ))),
        )
        interval = max(1, int(self.environment.get(
            "ODDS_SYNC_INTERVAL_MINUTES", "15"
        )))
        cycle = int(datetime.now(timezone.utc).timestamp() // (interval * 60))
        start = (cycle * batch_size) % len(keys)
        return tuple(keys[(start + offset) % len(keys)] for offset in range(batch_size))

    def _recent_raw_odds(
        self, *, hours: int
    ) -> list[SourceObservation]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, hours))
        rows = self.session.scalars(
            select(RawProviderPayloadRecord).where(
                RawProviderPayloadRecord.provider.in_((
                    "api_football", "the_odds_api",
                )),
                RawProviderPayloadRecord.resource == DataCapability.ODDS.value,
                RawProviderPayloadRecord.collected_at >= cutoff,
            ).order_by(
                RawProviderPayloadRecord.collected_at.desc()
            ).limit(5000)
        ).all()
        observations = [
            SourceObservation(
                provider=row.provider,
                capability=DataCapability.ODDS,
                external_id=row.external_id,
                values=row.payload,
                observed_at=row.collected_at,
            )
            for row in rows
        ]
        return observations

    def _recent_raw_fixtures(
        self, *, hours: int
    ) -> list[SourceObservation]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, hours))
        rows = self.session.scalars(
            select(RawProviderPayloadRecord).where(
                RawProviderPayloadRecord.resource
                == DataCapability.FIXTURES.value,
                RawProviderPayloadRecord.collected_at >= cutoff,
            ).order_by(
                RawProviderPayloadRecord.collected_at.desc()
            ).limit(20000)
        ).all()
        # O registro mais recente de cada identidade é suficiente para fusão;
        # versões anteriores apenas repetiriam trabalho e previsões.
        latest: dict[tuple[str, str], RawProviderPayloadRecord] = {}
        for row in rows:
            latest.setdefault((row.provider, row.external_id), row)
        observations = [
            SourceObservation(
                provider=row.provider,
                capability=DataCapability.FIXTURES,
                external_id=row.external_id,
                values=row.payload,
                observed_at=row.collected_at,
            )
            for row in latest.values()
        ]
        identity_keys = [
            f"match:{item.external_id}" for item in observations
        ]
        already_promoted = {
            (row.provider, row.external_id)
            for row in self.session.scalars(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.external_id.in_(identity_keys)
                )
            ).all()
        }
        external_ids = [item.external_id for item in observations]
        directly_promoted = {
            (source, external_id)
            for source, external_id in self.session.execute(
                select(Match.source, Match.external_id).where(
                    Match.external_id.in_(external_ids)
                )
            ).all()
        }
        pending = [
            item for item in observations
            if (item.provider, f"match:{item.external_id}")
            not in already_promoted
            and (item.provider, item.external_id) not in directly_promoted
        ]
        fusion = MatchFusionService(self.session)
        now = datetime.now(timezone.utc)

        def priority(item: SourceObservation) -> tuple[int, float]:
            adapted = fusion._adapt(item)
            if adapted is None:
                return (2, float("inf"))
            kickoff = (
                adapted.kickoff_at
                if adapted.kickoff_at.tzinfo
                else adapted.kickoff_at.replace(tzinfo=timezone.utc)
            )
            # Futuras e recentes primeiro; partidas antigas ficam no fim.
            return (0 if kickoff >= now - timedelta(hours=3) else 1,
                    abs((kickoff - now).total_seconds()))

        pending.sort(key=priority)
        batch_size = max(1, int(self.environment.get(
            "FIXTURE_RECOVERY_BATCH_SIZE", "500"
        )))
        return pending[:batch_size]

    def _run_stage(
        self,
        name: str,
        operation: Callable[[], object],
        failures: dict[str, str],
        default: Any,
    ) -> Any:
        """Executa um estágio derivado em savepoint independente."""
        try:
            with self.session.begin_nested():
                result = operation()
                self.session.flush()
            return result
        except Exception as error:
            failures[f"stage:{name}"] = (
                f"{type(error).__name__}: {error}"
            )
            return default

    def _collect_targeted_api_football_odds(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> tuple[SourceObservation, ...]:
        """Completa odds de jogos prioritários ausentes no lote diário."""
        source = next(
            (
                item for item in engine.sources
                if item.name == "api_football"
                and DataCapability.ODDS
                in getattr(item, "capabilities", ())
            ),
            None,
        )
        if source is None:
            return ()
        now = datetime.now(timezone.utc)
        candidates: list[tuple[int, datetime, str]] = []
        for observation in fixtures:
            if observation.provider != "api_football":
                continue
            row = observation.values
            if not self._fixture_is_modeled(row):
                continue
            fixture = row.get("fixture") or {}
            if str((fixture.get("status") or {}).get("short")) not in {
                "NS", "TBD"
            }:
                continue
            try:
                kickoff = datetime.fromisoformat(
                    str(fixture.get("date")).replace("Z", "+00:00")
                )
            except (TypeError, ValueError):
                continue
            if not now <= kickoff <= now + timedelta(days=14):
                continue
            fixture_id = str(fixture.get("id") or "")
            league = row.get("league") or {}
            policy = competition_policy(
                str(league.get("name") or ""),
                str(league.get("country") or ""),
            )
            if fixture_id:
                candidates.append((
                    competition_priority(policy) if policy else 40,
                    kickoff,
                    fixture_id,
                ))
        limit = max(
            0,
            int(self.environment.get(
                "AUTO_TARGETED_ODDS_MAX_PER_SYNC", "20"
            )),
        )
        collected: list[SourceObservation] = []
        for _, _, fixture_id in sorted(candidates)[:limit]:
            if not self._quota_allows(source):
                break
            try:
                collected.extend(source.collect(
                    DataCapability.ODDS, fixture=fixture_id
                ))
            except Exception:
                continue
        return tuple(collected)

    def _collect_post_match_statistics(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
        *,
        unavailable_sources: frozenset[str] = frozenset(),
    ) -> tuple[int, int]:
        """Coleta somente partidas encerradas ainda sem estatísticas."""
        promoted, promoted_settled = self._promote_raw_statistics()
        api_source = next(
            (
                source
                for source in engine.sources
                if source.name == "api_football"
                and source.name not in unavailable_sources
                and DataCapability.STATISTICS
                in getattr(source, "capabilities", ())
            ),
            None,
        )
        cutoff = datetime.now(timezone.utc).replace(
            tzinfo=None
        ) - timedelta(
            days=max(
                1,
                int(self.environment.get(
                    "AUTO_STATS_LOOKBACK_DAYS", "365"
                )),
            )
        )
        matches = self.session.scalars(
            select(Match)
            .outerjoin(
                MatchStatistics,
                MatchStatistics.match_id == Match.id,
            )
            .where(
                Match.status == "finished",
                Match.kickoff_at >= cutoff,
                MatchStatistics.id.is_(None),
            )
            .order_by(Match.kickoff_at.desc())
            .limit(max(100, int(self.environment.get(
                "AUTO_STATS_CANDIDATE_SCAN", "3000"
            ))))
        ).all()
        fixture_rows = {
            observation.external_id: observation
            for observation in fixtures
            if observation.provider == "api_football"
        }
        retry_cutoff = datetime.now(timezone.utc) - timedelta(
            hours=max(
                1,
                int(self.environment.get(
                    "AUTO_STATS_RETRY_HOURS", "1"
                )),
            )
        )
        competition_ids = {match.competition_id for match in matches}
        competitions = {
            item.id: item for item in self.session.scalars(
                select(Competition).where(
                    Competition.id.in_(competition_ids or {-1})
                )
            ).all()
        }
        candidates = []
        for match in matches:
            fixture_id = self._provider_match_id(
                match, "api_football"
            )
            if not fixture_id or api_source is None:
                continue
            attempted = self.session.scalar(
                select(exists().where(
                    RawProviderPayloadRecord.provider
                    == "api_football",
                    RawProviderPayloadRecord.resource
                    == "statistics_attempt",
                    RawProviderPayloadRecord.external_id == fixture_id,
                    RawProviderPayloadRecord.collected_at
                    >= retry_cutoff,
                ))
            )
            if attempted:
                continue
            fixture_observation = fixture_rows.get(fixture_id)
            if fixture_observation is None:
                raw = self.session.scalar(
                    select(RawProviderPayloadRecord)
                    .where(
                        RawProviderPayloadRecord.provider
                        == "api_football",
                        RawProviderPayloadRecord.resource == "fixtures",
                        RawProviderPayloadRecord.external_id
                        == fixture_id,
                    )
                    .order_by(
                        RawProviderPayloadRecord.collected_at.desc()
                    )
                )
                if raw is None:
                    continue
                fixture_observation = SourceObservation(
                    "api_football",
                    DataCapability.FIXTURES,
                    fixture_id,
                    raw.payload,
                    raw.collected_at,
                )
            has_pending_bet = self.session.scalar(
                select(exists().where(
                    Bet.match_id == match.id,
                    Bet.status == "pending",
                ))
            )
            candidates.append(
                (
                    not bool(has_pending_bet),
                    0 if (
                        (competition := competitions.get(match.competition_id))
                        and competition_is_modeled(competition)
                    ) else 1,
                    match,
                    fixture_id,
                    fixture_observation,
                )
            )

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
                -item[2].kickoff_at.timestamp(),
            )
        )
        limit = max(
            0,
            int(self.environment.get("AUTO_STATS_MAX_PER_SYNC", "100")),
        )
        pipeline = OperationalPipelineService(self.session)
        stored, settled = promoted, promoted_settled
        for _, _, _, fixture_id, fixture_observation in (
            candidates[:limit]
        ):
            if not self._quota_allows(api_source):
                break
            try:
                observations = api_source.collect(
                    DataCapability.STATISTICS,
                    fixture=fixture_id,
                )
                attempt_status = (
                    "received" if observations else "empty"
                )
            except Exception as error:
                observations = ()
                attempt_status = (
                    f"failed:{type(error).__name__}"
                )
            attempted_at = datetime.now(timezone.utc)
            self.raw_store.save(
                RawProviderPayload(
                    provider="api_football",
                    resource="statistics_attempt",
                    external_id=fixture_id,
                    payload={
                        "fixture_id": fixture_id,
                        "status": attempt_status,
                        "attempted_at": attempted_at.isoformat(),
                    },
                    collected_at=attempted_at,
                )
            )
            for observation in observations:
                self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=(
                            f"{fixture_id}:{observation.external_id}"
                        ),
                        payload=observation.values,
                        collected_at=observation.observed_at,
                    )
                )
            try:
                player_observations = api_source.collect(
                    DataCapability.PLAYER_STATISTICS,
                    fixture=fixture_id,
                )
            except Exception:
                player_observations = ()
            self._save_observations(
                player_observations,
                resource="player_statistics",
                prefix=fixture_id,
            )
            try:
                result = pipeline.process_post_match_statistics(
                    fixture_observation,
                    observations,
                )
            except ValueError:
                continue
            stored += result["statistics"]
            settled += result["settled_bets"]
        complementary = self._collect_sportmonks_statistics(
            engine,
            matches,
            unavailable_sources=unavailable_sources,
        )
        stored += complementary[0]
        settled += complementary[1]
        return stored, settled

    def _promote_raw_statistics(self) -> tuple[int, int]:
        """Reaproveita estatísticas brutas antes de consumir nova cota."""
        matches = self.session.scalars(
            select(Match)
            .outerjoin(
                MatchStatistics,
                MatchStatistics.match_id == Match.id,
            )
            .where(
                Match.status == "finished",
                MatchStatistics.id.is_(None),
            )
            .order_by(Match.kickoff_at.desc())
            .limit(max(1, int(self.environment.get(
                "AUTO_RAW_STATS_REPROCESS_LIMIT", "250"
            ))))
        ).all()
        pipeline = OperationalPipelineService(self.session)
        stored = settled = 0
        for match in matches:
            fixture_id = self._provider_match_id(match, "api_football")
            if not fixture_id:
                continue
            fixture_row = self.session.scalar(
                select(RawProviderPayloadRecord).where(
                    RawProviderPayloadRecord.provider == "api_football",
                    RawProviderPayloadRecord.resource.in_(
                        ("fixtures", "live", "live_details")
                    ),
                    RawProviderPayloadRecord.external_id.like(
                        f"%{fixture_id}%"
                    ),
                ).order_by(
                    RawProviderPayloadRecord.collected_at.desc()
                )
            )
            statistic_rows = self.session.scalars(
                select(RawProviderPayloadRecord).where(
                    RawProviderPayloadRecord.provider == "api_football",
                    RawProviderPayloadRecord.resource == "statistics",
                    RawProviderPayloadRecord.external_id.like(
                        f"{fixture_id}:%"
                    ),
                ).order_by(
                    RawProviderPayloadRecord.collected_at.desc()
                )
            ).all()
            if fixture_row is None or not statistic_rows:
                continue
            fixture = SourceObservation(
                "api_football",
                DataCapability.FIXTURES,
                fixture_id,
                fixture_row.payload,
                fixture_row.collected_at,
            )
            observations, seen = [], set()
            for row in statistic_rows:
                team_id = str(
                    (row.payload.get("team") or {}).get("id") or ""
                )
                if not team_id or team_id in seen:
                    continue
                seen.add(team_id)
                observations.append(SourceObservation(
                    "api_football",
                    DataCapability.STATISTICS,
                    team_id,
                    row.payload,
                    row.collected_at,
                ))
            result = pipeline.process_post_match_statistics(
                fixture, tuple(observations)
            )
            stored += result["statistics"]
            settled += result["settled_bets"]
        return stored, settled

    def _learn_from_finished_scores(self) -> dict[str, int]:
        """Audita mercados resolvíveis por placar, mesmo sem ficha detalhada.

        A rotina é incremental: partidas que já possuem qualquer auditoria do
        pipeline são reconsideradas com segurança, pois cada previsão é
        idempotente na camada de aprendizado.
        """
        limit = max(
            0,
            int(self.environment.get("AUTO_SCORE_LEARNING_MAX_PER_SYNC", "250")),
        )
        matches = self.session.scalars(
            select(Match)
            .where(
                Match.status == "finished",
                Match.home_score.is_not(None),
                Match.away_score.is_not(None),
                exists().where(
                    Prediction.match_id == Match.id,
                    ~exists().where(
                        Audit.prediction_id == Prediction.id,
                    ),
                ),
            )
            .order_by(Match.kickoff_at.desc())
            .limit(limit)
        ).all()
        service = LearningPipelineService(self.session)
        processed = audited = 0
        for match in matches:
            statistics = self.session.scalar(
                select(MatchStatistics).where(
                    MatchStatistics.match_id == match.id
                )
            )
            result = service.process(match, statistics)
            processed += 1
            audited += int(result["audited_predictions"])
        return {
            "matches_processed": processed,
            "predictions_audited": audited,
        }

    def _collect_sportmonks_statistics(
        self,
        engine: MultiSourceEngine,
        matches: list[Match],
        *,
        unavailable_sources: frozenset[str] = frozenset(),
    ) -> tuple[int, int]:
        source = next(
            (
                item for item in engine.sources
                if item.name == "sportmonks"
                and item.name not in unavailable_sources
                and DataCapability.STATISTICS
                in getattr(item, "capabilities", ())
            ),
            None,
        )
        if source is None:
            return 0, 0
        by_provider_id = {
            provider_id: match
            for match in matches
            if (
                provider_id := self._provider_match_id(
                    match, "sportmonks"
                )
            )
        }
        if not by_provider_id:
            return 0, 0
        dates = sorted(
            {
                match.kickoff_at.date().isoformat()
                for match in by_provider_id.values()
            },
            reverse=True,
        )[:2]
        observations: list[SourceObservation] = []
        for date in dates:
            try:
                observations.extend(
                    source.collect(
                        DataCapability.STATISTICS,
                        date=date,
                    )
                )
            except Exception:
                continue
        stored = settled = 0
        for observation in observations:
            match = by_provider_id.get(observation.external_id)
            if match is None:
                continue
            self.raw_store.save(
                RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
            )
            parsed = _sportmonks_match_statistics(
                observation.values, match
            )
            if parsed is None or not match.external_id:
                continue
            result = PostMatchService(self.session).settle_match(
                match_external_id=str(match.external_id),
                source="sportmonks",
                commit=False,
                **parsed,
            )
            stored += 1
            settled += len(result["settled_bets"])
        return stored, settled

    def _provider_match_id(
        self,
        match: Match,
        provider: str,
    ) -> str | None:
        if match.source == provider and match.external_id:
            return str(match.external_id)
        decision = self.session.scalar(
            select(IdentityDecisionRecord)
            .where(
                IdentityDecisionRecord.provider == provider,
                IdentityDecisionRecord.candidate_id
                == f"match:{match.id}",
                IdentityDecisionRecord.status == "matched",
            )
            .order_by(
                IdentityDecisionRecord.decided_at.desc()
            )
        )
        if decision is None:
            return None
        prefix = "match:"
        return (
            decision.external_id[len(prefix):]
            if decision.external_id.startswith(prefix)
            else decision.external_id
        )

    def _persist_live_snapshots(
        self,
        fixtures: tuple[SourceObservation, ...],
    ) -> int:
        engine = LiveEngine()
        store = LiveStore(self.session)
        captured = datetime.now(timezone.utc)
        saved = 0
        for observation in fixtures:
            live_values = _provider_live_values(observation)
            if live_values is None:
                continue
            external_id, minute, home_goals, away_goals = live_values
            decision = self.session.scalar(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.provider
                    == observation.provider,
                    IdentityDecisionRecord.external_id
                    == f"match:{external_id}",
                    IdentityDecisionRecord.status == "matched",
                )
            )
            match_id = (
                decision.candidate_id.removeprefix("match:")
                if decision and decision.candidate_id
                else f"{observation.provider}:{external_id}"
            )
            latest = store.latest(match_id)
            state = (
                LiveMatchState(
                    match_id=match_id,
                    phase=LivePhase(latest.phase),
                    health=LiveHealth(latest.health),
                    minute=latest.minute,
                    home_score=latest.home_score,
                    away_score=latest.away_score,
                    statistics={
                        key: Decimal(str(value))
                        for key, value in latest.statistics.items()
                    },
                    odds={
                        key: Decimal(str(value))
                        for key, value in latest.odds.items()
                    },
                    probabilities={
                        key: Decimal(str(value))
                        for key, value in latest.probabilities.items()
                    },
                    recommendations=tuple(
                        LiveRecommendation(
                            str(item["selection"]),
                            Decimal(str(item["probability"])),
                            Decimal(str(item["odds"])),
                            Decimal(str(item["expected_value"])),
                        )
                        for item in latest.recommendations
                    ),
                    anomalies=tuple(latest.anomalies),
                    push_messages=(),
                    processed_event_ids=tuple(
                        self.session.scalars(
                            select(LiveEventRecord.id).where(
                                LiveEventRecord.match_id == match_id
                            )
                        ).all()
                    ),
                    last_event_at=latest.captured_at,
                    revision=latest.revision,
                )
                if latest else engine.initial(match_id)
            )
            for suffix, kind, payload in (
                (
                    "score",
                    LiveEventType.SCORE,
                    {
                        "home": home_goals,
                        "away": away_goals,
                    },
                ),
                ("clock", LiveEventType.CLOCK, {"minute": minute}),
            ):
                event = LiveEvent(
                    (
                        f"{match_id}:{suffix}:{minute}:"
                        f"{home_goals}:{away_goals}:"
                        f"{observation.provider}"
                    ),
                    match_id,
                    kind,
                    captured,
                    captured,
                    payload,
                )
                store.save_event(event)
                state = engine.ingest(state, event)
            if latest is None or state.revision > latest.revision:
                store.save_snapshot(state, captured)
                saved += 1
        return saved

    def _collect_lineups(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> int:
        lineup_sources = [
            source for source in engine.sources
            if DataCapability.LINEUPS
            in getattr(source, "capabilities", ())
        ]
        api_source = next(
            (
                source for source in lineup_sources
                if source.name == "api_football"
            ),
            None,
        )
        now = datetime.now(timezone.utc)
        candidates: list[tuple[datetime, str]] = []
        for observation in fixtures:
            if observation.provider != "api_football":
                continue
            fixture = observation.values.get("fixture", {})
            status = fixture.get("status", {})
            if status.get("short") not in {
                "NS", "TBD", "1H", "HT", "2H", "ET", "BT", "P", "LIVE"
            }:
                continue
            fixture_id = str(fixture.get("id") or "")
            try:
                kickoff = datetime.fromisoformat(
                    str(fixture.get("date")).replace("Z", "+00:00")
                )
            except (TypeError, ValueError):
                continue
            if fixture_id and now - timedelta(hours=1) <= kickoff <= now + timedelta(hours=2):
                recent_cutoff = now - timedelta(minutes=20)
                already_collected = self.session.scalar(
                    select(
                        exists().where(
                            RawProviderPayloadRecord.provider == "api_football",
                            RawProviderPayloadRecord.resource == "lineups",
                            RawProviderPayloadRecord.external_id.like(
                                f"{fixture_id}:%"
                            ),
                            RawProviderPayloadRecord.collected_at
                            >= recent_cutoff,
                        )
                    )
                )
                if already_collected:
                    continue
                candidates.append((kickoff, fixture_id))
        saved = 0
        limit = max(
            0,
            int(self.environment.get("AUTO_LINEUPS_MAX_PER_SYNC", "100")),
        )
        for _, fixture_id in (
            sorted(candidates)[:limit] if api_source else []
        ):
            for observation in api_source.collect(
                DataCapability.LINEUPS, fixture=fixture_id
            ):
                if self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=f"{fixture_id}:{observation.external_id}",
                        payload=observation.values,
                        collected_at=observation.observed_at,
                    )
                ):
                    saved += 1
        for source in lineup_sources:
            if source.name == "api_football":
                continue
            try:
                observations = source.collect(
                    DataCapability.LINEUPS,
                    date=now.date().isoformat(),
                )
            except Exception:
                continue
            for observation in observations:
                payload = observation.values
                if not isinstance(payload, dict) or not payload.get(
                    "lineups"
                ):
                    continue
                if self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=observation.external_id,
                        payload=payload,
                        collected_at=observation.observed_at,
                    )
                ):
                    saved += 1
        return saved

    def _collect_api_football_enrichment(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> dict[str, int]:
        """Coleta recursos Ultra sem torná-los autoridade canônica exclusiva."""
        source = next(
            (
                item for item in engine.sources
                if item.name == "api_football"
            ),
            None,
        )
        if (
            source is None
            or DataCapability.COVERAGE
            not in getattr(source, "capabilities", ())
        ):
            return {}
        now = datetime.now(timezone.utc)
        counters = {
            "coverage": 0,
            "injuries": 0,
            "team_statistics": 0,
            "provider_predictions": 0,
            "quota_snapshots": 0,
        }

        if not self._resource_recent("coverage", "current", hours=24):
            observations = source.collect(
                DataCapability.COVERAGE,
                current="true",
            )
            observations = tuple(
                item for item in observations
                if self._coverage_is_modeled(item.values)
            )
            counters["coverage"] += self._save_observations(
                observations, resource="coverage", prefix="current"
            )

        today = now.date().isoformat()
        if not self._resource_recent("injuries", today, hours=6):
            observations = source.collect(
                DataCapability.INJURIES,
                date=today,
                timezone="America/Sao_Paulo",
            )
            counters["injuries"] += self._save_observations(
                observations, resource="injuries", prefix=today
            )

        limit = max(
            0,
            int(self.environment.get("AUTO_ENRICHMENT_MAX_PER_SYNC", "100")),
        )
        api_fixtures = [
            item for item in fixtures
            if item.provider == "api_football"
            and self._fixture_is_modeled(item.values)
        ][:limit]
        team_targets: set[tuple[str, str, str]] = set()
        for item in api_fixtures:
            if not self._quota_allows(source):
                break
            row = item.values
            fixture_id = str((row.get("fixture") or {}).get("id") or "")
            league = row.get("league") or {}
            league_id = str(league.get("id") or "")
            season = str(league.get("season") or "")
            if (
                fixture_id
                and not self._resource_recent(
                    "provider_predictions", fixture_id, hours=6
                )
            ):
                observations = source.collect(
                    DataCapability.PROVIDER_PREDICTIONS,
                    fixture=fixture_id,
                )
                counters["provider_predictions"] += self._save_observations(
                    observations,
                    resource="provider_predictions",
                    prefix=fixture_id,
                )
            for team in (row.get("teams") or {}).values():
                team_id = str((team or {}).get("id") or "")
                if team_id and league_id and season:
                    team_targets.add((team_id, league_id, season))

        for team_id, league_id, season in sorted(team_targets)[:limit]:
            if not self._quota_allows(source):
                break
            identity = f"{team_id}:{league_id}:{season}"
            if self._resource_recent("team_statistics", identity, hours=12):
                continue
            observations = source.collect(
                DataCapability.TEAM_STATISTICS,
                team=team_id,
                league=league_id,
                season=season,
                date=today,
            )
            counters["team_statistics"] += self._save_observations(
                observations,
                resource="team_statistics",
                prefix=identity,
            )

        counters["quota_snapshots"] += self._persist_quota_snapshot(source)
        return counters

    def _collect_live_details(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> dict[str, int]:
        """Obtém ficha rica em lote e odds ao vivo com poucas requisições."""
        source = next(
            (
                item for item in engine.sources
                if item.name == "api_football"
            ),
            None,
        )
        if (
            source is None
            or DataCapability.FIXTURES
            not in getattr(source, "capabilities", ())
        ):
            return {}
        limit = max(
            1,
            int(self.environment.get(
                "AUTO_LIVE_DETAILS_MAX_PER_SYNC", "30"
            )),
        )
        fixture_ids = [
            str((item.values.get("fixture") or {}).get("id") or "")
            for item in fixtures
            if item.provider == "api_football"
        ]
        fixture_ids = [item for item in fixture_ids if item][:limit]
        details_saved = odds_saved = 0
        statistics_saved = events_saved = lineups_saved = 0
        canonical_statistics = 0
        if fixture_ids:
            if not self._quota_allows(source):
                return {
                    "fixtures": len(fixture_ids),
                    "details": 0,
                    "live_odds": 0,
                    "quota_snapshots": self._persist_quota_snapshot(source),
                    "quota_guard": 1,
                }
            # A API-Football aceita no máximo 20 IDs por requisição.
            # Partidas simultâneas acima disso são divididas em lotes, sem
            # descartar ligas ou gerar resposta 422.
            for start in range(0, len(fixture_ids), 20):
                if not self._quota_allows(source):
                    break
                observations = source.collect(
                    DataCapability.FIXTURES,
                    ids="-".join(fixture_ids[start:start + 20]),
                    timezone="America/Sao_Paulo",
                )
                details_saved += self._save_observations(
                    observations,
                    resource="live_details",
                    prefix=datetime.now(timezone.utc).strftime("%Y%m%d%H%M"),
                )
            fixture_by_id = {
                str((item.values.get("fixture") or {}).get("id")): item
                for item in fixtures
                if item.provider == "api_football"
            }
            for fixture_id in fixture_ids:
                if not self._quota_allows(source):
                    break
                try:
                    statistics = source.collect(
                        DataCapability.STATISTICS, fixture=fixture_id
                    )
                    statistics_saved += self._save_observations(
                        statistics,
                        resource="statistics",
                        prefix=fixture_id,
                    )
                    fixture = fixture_by_id.get(fixture_id)
                    if fixture is not None:
                        canonical_statistics += (
                            OperationalPipelineService(
                                self.session
                            ).process_live_statistics(fixture, statistics)
                        )
                except Exception:
                    statistics = ()
                try:
                    events = source.collect(
                        DataCapability.EVENTS, fixture=fixture_id
                    )
                    events_saved += self._save_observations(
                        events, resource="events", prefix=fixture_id
                    )
                except Exception:
                    pass
                try:
                    lineups = source.collect(
                        DataCapability.LINEUPS, fixture=fixture_id
                    )
                    lineups_saved += self._save_observations(
                        lineups, resource="lineups", prefix=fixture_id
                    )
                except Exception:
                    pass
            try:
                live_odds = source.collect(DataCapability.LIVE_ODDS)
            except Exception:
                live_odds = ()
            odds_saved += self._save_observations(
                live_odds,
                resource="live_odds",
            )
        quota = self._persist_quota_snapshot(source)
        return {
            "fixtures": len(fixture_ids),
            "details": details_saved,
            "live_odds": odds_saved,
            "statistics": statistics_saved,
            "canonical_statistics": canonical_statistics,
            "events": events_saved,
            "lineups": lineups_saved,
            "quota_snapshots": quota,
        }

    def _save_observations(
        self,
        observations: tuple[SourceObservation, ...],
        *,
        resource: str,
        prefix: str | None = None,
    ) -> int:
        saved = 0
        for observation in observations:
            external_id = (
                f"{prefix}:{observation.external_id}"
                if prefix else observation.external_id
            )
            saved += self.raw_store.save(
                RawProviderPayload(
                    provider=observation.provider,
                    resource=resource,
                    external_id=external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
            )
        return saved

    def _resource_recent(
        self,
        resource: str,
        external_id: str,
        *,
        hours: int,
    ) -> bool:
        return bool(self.session.scalar(
            select(exists().where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == resource,
                RawProviderPayloadRecord.external_id.like(
                    f"{external_id}%"
                ),
                RawProviderPayloadRecord.collected_at
                >= datetime.now(timezone.utc) - timedelta(hours=hours),
            ))
        ))

    def _persist_quota_snapshot(self, source: object) -> int:
        values = dict(getattr(source, "last_rate_limit", {}) or {})
        if not values:
            return 0
        now = datetime.now(timezone.utc)
        saved = self.raw_store.save(
            RawProviderPayload(
                provider="api_football",
                resource="quota",
                external_id=now.strftime("%Y-%m-%dT%H:%M"),
                payload=values,
                collected_at=now,
            )
        )
        return int(saved)

    def _quota_allows(self, source: object) -> bool:
        values = dict(getattr(source, "last_rate_limit", {}) or {})
        remaining = values.get("x-ratelimit-requests-remaining")
        if remaining is None:
            return True
        try:
            remaining_value = int(remaining)
        except (TypeError, ValueError):
            return True
        reserve = max(
            0,
            int(self.environment.get(
                "API_FOOTBALL_MIN_REMAINING", "7500"
            )),
        )
        return remaining_value > reserve

    def _fixture_is_modeled(self, row: Mapping[str, Any]) -> bool:
        league = row.get("league") or {}
        if competition_policy(
            str(league.get("name") or ""),
            str(league.get("country") or ""),
        ) is not None:
            return True
        external_id = str(league.get("id") or "")
        competition = self.session.scalar(select(Competition).where(
            Competition.source == "api_football",
            Competition.external_id == external_id,
        )) if external_id else None
        return competition_is_modeled(competition)

    def _coverage_is_modeled(self, row: Mapping[str, Any]) -> bool:
        league = row.get("league") or {}
        country = row.get("country") or {}
        if competition_policy(
            str(league.get("name") or ""),
            str(country.get("name") or ""),
        ) is not None:
            return True
        competition = self.session.scalar(select(Competition).where(
            Competition.name == str(league.get("name") or ""),
            Competition.country == (str(country.get("name") or "") or None),
        ))
        return competition_is_modeled(competition)

    def _reconcile_stale_matches(
        self,
        live_observations: tuple[SourceObservation, ...] = (),
    ) -> int:
        # Proteção contra provedores que mantêm o status ao vivo depois do
        # apito final. Três horas ainda cobrem intervalo, acréscimos e
        # prorrogação sem deixar partidas encerradas presas no painel.
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
        active_match_ids: set[int] = set()
        for observation in live_observations:
            decision = self.session.scalar(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.provider
                    == observation.provider,
                    IdentityDecisionRecord.external_id
                    == f"match:{observation.external_id}",
                )
            )
            if decision and decision.candidate_id:
                active_match_ids.add(int(
                    decision.candidate_id.removeprefix("match:")
                ))
                continue
            direct = self.session.scalar(select(Match.id).where(
                Match.source == observation.provider,
                Match.external_id == observation.external_id,
            ))
            if direct is not None:
                active_match_ids.add(direct)
        statement = select(Match).where(
            Match.status == "in_progress",
            Match.kickoff_at < cutoff,
        )
        if active_match_ids:
            statement = statement.where(
                Match.id.not_in(active_match_ids)
            )
        stale = self.session.scalars(
            statement
        ).all()
        for match in stale:
            match.status = "finished"
        return len(stale)

    def _fixture_parameters(self) -> dict[str, str]:
        now = datetime.now(ZoneInfo("America/Sao_Paulo"))
        return {
            "date": now.date().isoformat(),
            "league": self.environment.get("OPENLIGADB_LEAGUE", "bl1"),
            "season": self.environment.get("OPENLIGADB_SEASON", str(now.year)),
            "path": self.environment.get(
                "FOOTBALL_DATA_UK_PATH",
                "mmz4281/2526/E0.csv",
            ),
        }


def _provider_live_values(
    observation: SourceObservation,
) -> tuple[str, int, int, int] | None:
    row = observation.values
    if observation.provider == "api_football":
        fixture = row.get("fixture") or {}
        status = fixture.get("status") or {}
        if status.get("short") not in {
            "1H", "HT", "2H", "ET", "BT", "P", "LIVE"
        }:
            return None
        goals = row.get("goals") or {}
        return (
            str(fixture.get("id") or observation.external_id),
            int(status.get("elapsed") or 0),
            int(goals.get("home") or 0),
            int(goals.get("away") or 0),
        )
    if observation.provider == "sportmonks":
        state = row.get("state") or {}
        state_name = str(
            state.get("short_name") or state.get("name") or ""
        ).casefold()
        if not any(
            token in state_name
            for token in ("live", "inplay", "1st", "2nd", "half")
        ):
            return None
        scores = _sportmonks_scores(row)
        return (
            observation.external_id,
            int(row.get("length") or row.get("minute") or 0),
            scores.get("home", 0),
            scores.get("away", 0),
        )
    return None


def _sportmonks_match_statistics(
    row: Mapping[str, object],
    match: Match,
) -> dict[str, object] | None:
    participants = row.get("participants")
    statistics = row.get("statistics")
    if not isinstance(participants, list) or not isinstance(
        statistics, list
    ):
        return None
    locations = {
        str(item.get("id")): str(
            (item.get("meta") or {}).get("location") or ""
        ).casefold()
        for item in participants
        if isinstance(item, dict) and item.get("id") is not None
    }
    values: dict[str, dict[str, object]] = {
        "home": {},
        "away": {},
    }
    for item in statistics:
        if not isinstance(item, dict):
            continue
        location = locations.get(str(item.get("participant_id")))
        if location not in values:
            continue
        stat_type = item.get("type") or {}
        if not isinstance(stat_type, dict):
            continue
        name = str(
            stat_type.get("developer_name")
            or stat_type.get("name")
            or ""
        ).casefold().replace(" ", "_")
        data = item.get("data")
        value = (
            data.get("value")
            if isinstance(data, dict)
            else item.get("value")
        )
        if name and value is not None:
            values[location][name] = value
    if not values["home"] and not values["away"]:
        return None
    scores = _sportmonks_scores(row)
    home_score = (
        int(match.home_score)
        if match.home_score is not None
        else scores.get("home")
    )
    away_score = (
        int(match.away_score)
        if match.away_score is not None
        else scores.get("away")
    )
    if home_score is None or away_score is None:
        return None

    def stat(
        location: str,
        *names: str,
        percentage: bool = False,
    ) -> int | float | None:
        for name in names:
            value = values[location].get(name)
            if value is None:
                continue
            try:
                number = float(str(value).rstrip("%"))
                return number if percentage else int(number)
            except (TypeError, ValueError):
                continue
        return None

    return {
        "home_score": home_score,
        "away_score": away_score,
        "corners_home": stat("home", "corners", "corner_kicks"),
        "corners_away": stat("away", "corners", "corner_kicks"),
        "yellow_cards_home": stat("home", "yellowcards", "yellow_cards"),
        "yellow_cards_away": stat("away", "yellowcards", "yellow_cards"),
        "red_cards_home": stat("home", "redcards", "red_cards"),
        "red_cards_away": stat("away", "redcards", "red_cards"),
        "shots_home": stat("home", "shots_total", "total_shots"),
        "shots_away": stat("away", "shots_total", "total_shots"),
        "shots_on_target_home": stat(
            "home", "shots_on_target", "shots_ongoal"
        ),
        "shots_on_target_away": stat(
            "away", "shots_on_target", "shots_ongoal"
        ),
        "offsides_home": stat("home", "offsides"),
        "offsides_away": stat("away", "offsides"),
        "possession_home": stat(
            "home", "ball_possession", "possessiontime",
            percentage=True,
        ),
        "possession_away": stat(
            "away", "ball_possession", "possessiontime",
            percentage=True,
        ),
        "xg_home": stat(
            "home", "expected_goals", "xg", percentage=True
        ),
        "xg_away": stat(
            "away", "expected_goals", "xg", percentage=True
        ),
    }


def _sportmonks_scores(
    row: Mapping[str, object],
) -> dict[str, int]:
    participants = row.get("participants")
    scores = row.get("scores")
    if not isinstance(participants, list) or not isinstance(scores, list):
        return {}
    locations = {
        str(item.get("id")): str(
            (item.get("meta") or {}).get("location") or ""
        ).casefold()
        for item in participants
        if isinstance(item, dict)
    }
    result: dict[str, int] = {}
    for item in scores:
        if not isinstance(item, dict):
            continue
        location = locations.get(str(item.get("participant_id")))
        score = item.get("score") or {}
        goals = score.get("goals") if isinstance(score, dict) else None
        if location in {"home", "away"} and goals is not None:
            try:
                result[location] = max(
                    result.get(location, 0), int(goals)
                )
            except (TypeError, ValueError):
                continue
    return result
