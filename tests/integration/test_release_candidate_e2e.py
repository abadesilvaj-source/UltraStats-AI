from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.core.config import settings
from ultrastats_ai.domain.experience import (
    ExperienceMode,
    Notification,
    NotificationChannel,
    UserExperienceProfile,
)
from ultrastats_ai.domain.live import LiveEngine, LiveEvent, LiveEventType
from ultrastats_ai.domain.operations import QueueMessage, append_audit, create_backup
from ultrastats_ai.domain.prediction import ModelSpecification, PoissonScoreModel
from ultrastats_ai.domain.recommendation import (
    OddsQuote,
    OpportunityInput,
    RecommendationEngine,
)
from ultrastats_ai.domain.risk import (
    BetCandidate,
    PerformanceMetrics,
    RiskPortfolioEngine,
    RiskProfile,
    RiskProfileKind,
)
from ultrastats_ai.domain.statistics import MatchSample, StatisticalEngine
from ultrastats_ai.infrastructure.database.models import CanonicalBase
from ultrastats_ai.infrastructure.experience import ExperienceStore
from ultrastats_ai.infrastructure.live import LiveStore
from ultrastats_ai.infrastructure.operations import OperationsStore
from ultrastats_ai.infrastructure.prediction import PredictiveModelStore
from ultrastats_ai.infrastructure.recommendation import RecommendationStore
from ultrastats_ai.infrastructure.risk import RiskPortfolioStore
from ultrastats_ai.infrastructure.statistics import StatisticalSnapshotStore


NOW = datetime.now(timezone.utc)


def test_clean_database_migrates_through_the_complete_chain(tmp_path) -> None:
    database = tmp_path / "release.db"
    previous = settings.database_url
    settings.database_url = f"sqlite:///{database.as_posix()}"
    try:
        config = Config("alembic.ini")
        command.upgrade(config, "head")
        engine = create_engine(settings.database_url)
        try:
            tables = set(inspect(engine).get_table_names())
            assert {
                "statistical_snapshots",
                "predictive_models",
                "recommendation_opportunities",
                "risk_profiles",
                "user_experience_profiles",
                "live_events",
                "operational_metrics",
            } <= tables
        finally:
            engine.dispose()
    finally:
        settings.database_url = previous


def test_end_to_end_analytical_and_operational_flow() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            sample = MatchSample(
                "historical",
                "home",
                "league",
                NOW - timedelta(days=1),
                True,
                D("2"),
                D("1"),
                D("1.8"),
                D("1.0"),
                D(".7"),
                D("3"),
            )
            snapshot = StatisticalEngine(target_sample=1).calculate("home", (sample,), NOW)
            StatisticalSnapshotStore(session).save(snapshot)

            specification = ModelSpecification("poisson", "rc1", "league", "1x2", {})
            prediction_store = PredictiveModelStore(session)
            assert prediction_store.register(specification)
            forecast = PoissonScoreModel(specification, max_goals=6).predict(
                snapshot.metrics["expected_goals_for"],
                snapshot.metrics["expected_goals_against"],
            )
            prediction_store.save_forecast("match", forecast, NOW)

            probability = forecast.probabilities["home"]
            opportunity = RecommendationEngine().evaluate(
                OpportunityInput(
                    "match",
                    "1x2",
                    "home",
                    probability,
                    D(".95"),
                    D(".95"),
                    (OddsQuote("book", D("4"), NOW),),
                    "match",
                ),
                NOW,
            )
            assert opportunity.safe
            RecommendationStore(session).save(opportunity)

            profile = RiskProfile.preset(RiskProfileKind.MODERATE)
            plan = RiskPortfolioEngine(profile).optimize(
                D("1000"),
                (
                    BetCandidate(
                        "recommendation",
                        "league",
                        "1x2",
                        "match",
                        probability,
                        D("4"),
                        opportunity.score,
                    ),
                ),
            )
            assert plan.positions
            risk_store = RiskPortfolioStore(session)
            risk_store.save_profile("user", profile, NOW)
            risk_store.save_snapshot(
                "user",
                plan,
                PerformanceMetrics(plan.total_exposure, D("0"), D("0"), D("0"), D("0")),
                NOW,
            )

            experience_store = ExperienceStore(session)
            experience_store.save_profile(
                UserExperienceProfile("user", ExperienceMode.ADVANCED), NOW
            )
            experience_store.notify(
                Notification(
                    "notification",
                    "user",
                    "Opportunity",
                    "A recommendation is ready.",
                    NotificationChannel.IN_APP,
                    NOW,
                )
            )

            live_engine = LiveEngine()
            previous = live_engine.initial("match")
            live_event = LiveEvent(
                "goal",
                "match",
                LiveEventType.SCORE,
                NOW,
                NOW,
                {"home": 1, "away": 0},
            )
            current = live_engine.ingest(previous, live_event)
            live_store = LiveStore(session)
            live_store.save_event(live_event)
            live_store.save_snapshot(current, NOW)
            live_store.record_effects(previous, current, live_event.event_id, NOW)

            operations = OperationsStore(session)
            operations.metric("release.e2e", 1, {"version": "0.1.0-rc.1"}, NOW)
            operations.audit(append_audit((), "release_e2e", "codex", NOW)[0])
            operations.backup(create_backup({"match": "match"}, NOW), "memory://release")
            operations.enqueue("release", QueueMessage("release-message", {"ok": True}), NOW)
            session.commit()

            assert StatisticalSnapshotStore(session).latest("home") is not None
            assert RecommendationStore(session).safe_history()
            assert RiskPortfolioStore(session).history("user")
            assert ExperienceStore(session).notification_feed("user")
            assert LiveStore(session).latest("match") is not None
            assert OperationsStore(session).latest_metrics()
    finally:
        engine.dispose()
