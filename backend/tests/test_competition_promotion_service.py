from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.competition_catalog import (
    competition_is_modeled,
    competition_metadata,
)
from app.database.base import Base
from app.models import (
    Competition,
    Market,
    Match,
    MatchStatistics,
    Odd,
    Team,
)
from app.services.competition_promotion_service import (
    CompetitionPromotionService,
)


def test_observation_competition_is_promoted_after_sustained_coverage():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(
            name="Liga Regional Teste",
            country="Brasil",
            source="api_football",
            external_id="9001",
        )
        catalog_core = Competition(
            name="Premier League", country="England"
        )
        home, away = Team(name="Casa"), Team(name="Fora")
        market = Market(
            code="match_winner", name="Resultado", category="result"
        )
        session.add_all((competition, catalog_core, home, away, market))
        session.flush()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for index in range(20):
            match = Match(
                competition_id=competition.id,
                home_team_id=home.id,
                away_team_id=away.id,
                kickoff_at=now - timedelta(days=index + 1),
                status="finished",
                home_score=1,
                away_score=0,
            )
            session.add(match)
            session.flush()
            session.add(MatchStatistics(match_id=match.id))
        for index in range(5):
            match = Match(
                competition_id=competition.id,
                home_team_id=home.id,
                away_team_id=away.id,
                kickoff_at=now + timedelta(days=index + 1),
                status="scheduled",
            )
            session.add(match)
            session.flush()
            session.add(Odd(
                match_id=match.id,
                market_id=market.id,
                bookmaker="Book",
                selection="Home",
                odd_value=Decimal("2.00"),
                collected_at=now,
            ))
        session.flush()

        result = CompetitionPromotionService(session, {
            "AUTO_CORE_WINDOW_DAYS": "30",
            "AUTO_CORE_SUSTAIN_DAYS": "0",
            "AUTO_CORE_MIN_FINISHED_MATCHES": "20",
            "AUTO_CORE_MIN_ODDS_MATCHES": "5",
            "AUTO_CORE_STATISTICS_COVERAGE": "0.90",
            "AUTO_CORE_ODDS_COVERAGE": "0.80",
        }).evaluate()

        assert result["promoted_ids"] == [competition.id]
        assert competition.auto_core is True
        assert competition.promotion_status == "promoted"
        assert competition_is_modeled(competition) is True
        assert competition_metadata(
            competition.name, competition.country, auto_core=True
        )["group"] == "core"
        # O catálogo existente continua sendo a autoridade e não recebe estado
        # dinâmico nem alteração de grupo.
        assert catalog_core.auto_core is False
        assert catalog_core.promotion_status == "observation"
        assert competition_is_modeled(catalog_core) is True


def test_competition_loses_candidate_state_before_promotion_if_coverage_drops():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(
            name="Liga Sem Cobertura",
            promotion_status="candidate",
            promotion_qualified_since=(
                datetime.now(timezone.utc).replace(tzinfo=None)
                - timedelta(days=3)
            ),
        )
        session.add(competition)
        session.flush()

        result = CompetitionPromotionService(session, {
            "AUTO_CORE_SUSTAIN_DAYS": "7",
        }).evaluate()

        assert result["promoted"] == 0
        assert competition.auto_core is False
        assert competition.promotion_status == "observation"
        assert competition.promotion_qualified_since is None
