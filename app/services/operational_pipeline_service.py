from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Competition, Market, Match, Odd, Prediction, Team
from app.utils.betting_math import (
    calculate_expected_value,
    calculate_implied_probability,
)
from ultrastats_ai.domain.prediction import ModelSpecification, PoissonScoreModel
from ultrastats_ai.infrastructure.providers import DataCapability, SourceObservation


MARKETS = (
    ("match_winner", "Resultado da Partida", "result"),
    ("over_2_5_goals", "Mais de 2.5 Gols", "goals"),
    ("under_2_5_goals", "Menos de 2.5 Gols", "goals"),
    ("both_teams_to_score", "Ambas as Equipes Marcam", "goals"),
)

STATUS_MAP = {
    "NS": "scheduled",
    "TBD": "scheduled",
    "PST": "postponed",
    "CANC": "cancelled",
    "ABD": "cancelled",
    "FT": "finished",
    "AET": "finished",
    "PEN": "finished",
    "1H": "in_progress",
    "HT": "in_progress",
    "2H": "in_progress",
    "ET": "in_progress",
    "BT": "in_progress",
    "P": "in_progress",
    "LIVE": "in_progress",
}


class OperationalPipelineService:
    """Promove observações API-Football para as tabelas usadas pelo dashboard."""

    model_version = "operational-poisson-v1"

    def __init__(self, session: Session) -> None:
        self.session = session

    def process(
        self,
        *,
        fixtures: tuple[SourceObservation, ...],
        odds: tuple[SourceObservation, ...] = (),
    ) -> dict[str, int]:
        counters = {
            "competitions": 0,
            "teams": 0,
            "matches": 0,
            "markets": 0,
            "odds": 0,
            "predictions": 0,
        }
        markets = self._ensure_markets(counters)
        matches: dict[str, Match] = {}
        for observation in fixtures:
            if (
                observation.provider != "api_football"
                or observation.capability is not DataCapability.FIXTURES
            ):
                continue
            match = self._promote_fixture(observation.values, counters)
            if match is not None:
                matches[str(match.external_id)] = match

        self.session.flush()
        counters["odds"] += self._promote_odds(odds, matches, markets)
        self.session.flush()
        for match in matches.values():
            if match.status in {"scheduled", "in_progress"}:
                counters["predictions"] += self._predict(match, markets)
        return counters

    def _ensure_markets(self, counters: dict[str, int]) -> dict[str, Market]:
        result: dict[str, Market] = {}
        for code, name, category in MARKETS:
            market = self.session.scalar(select(Market).where(Market.code == code))
            if market is None:
                market = Market(code=code, name=name, category=category, active=True)
                self.session.add(market)
                self.session.flush()
                counters["markets"] += 1
            result[code] = market
        return result

    def _promote_fixture(
        self,
        row: Any,
        counters: dict[str, int],
    ) -> Match | None:
        if not isinstance(row, dict):
            return None
        fixture = row.get("fixture")
        league = row.get("league")
        teams = row.get("teams")
        if not all(isinstance(value, dict) for value in (fixture, league, teams)):
            return None
        home_data, away_data = teams.get("home"), teams.get("away")
        if not isinstance(home_data, dict) or not isinstance(away_data, dict):
            return None
        external_id = str(fixture.get("id", "")).strip()
        if not external_id:
            return None

        competition = self._competition(league, counters)
        home = self._team(home_data, league, counters)
        away = self._team(away_data, league, counters)
        if home.id == away.id:
            return None
        kickoff = datetime.fromisoformat(str(fixture["date"]).replace("Z", "+00:00"))
        status_data = fixture.get("status") if isinstance(fixture.get("status"), dict) else {}
        goals = row.get("goals") if isinstance(row.get("goals"), dict) else {}
        venue_data = fixture.get("venue") if isinstance(fixture.get("venue"), dict) else {}
        match = self.session.scalar(
            select(Match).where(Match.external_id == external_id)
        )
        if match is None:
            match = Match(
                competition_id=competition.id,
                home_team_id=home.id,
                away_team_id=away.id,
                kickoff_at=kickoff,
                source="api_football",
                external_id=external_id,
            )
            self.session.add(match)
            counters["matches"] += 1
        match.competition_id = competition.id
        match.home_team_id = home.id
        match.away_team_id = away.id
        match.kickoff_at = kickoff
        match.status = STATUS_MAP.get(str(status_data.get("short", "")), "scheduled")
        match.home_score = _optional_int(goals.get("home"))
        match.away_score = _optional_int(goals.get("away"))
        match.venue = str(venue_data.get("name") or "") or None
        return match

    def _competition(self, league: dict[str, Any], counters: dict[str, int]) -> Competition:
        external_id = str(league.get("id"))
        competition = self.session.scalar(
            select(Competition).where(
                Competition.source == "api_football",
                Competition.external_id == external_id,
            )
        )
        if competition is None:
            competition = Competition(
                name=str(league.get("name") or f"League {external_id}"),
                country=str(league.get("country") or "") or None,
                season=str(league.get("season") or "") or None,
                sport="football",
                source="api_football",
                external_id=external_id,
                active=True,
            )
            self.session.add(competition)
            self.session.flush()
            counters["competitions"] += 1
        return competition

    def _team(
        self,
        data: dict[str, Any],
        league: dict[str, Any],
        counters: dict[str, int],
    ) -> Team:
        external_id = str(data.get("id"))
        name = str(data.get("name") or f"Team {external_id}")
        team = self.session.scalar(
            select(Team).where(
                Team.source == "api_football",
                Team.external_id == external_id,
            )
        )
        if team is None:
            team = self.session.scalar(select(Team).where(Team.name == name))
        if team is None:
            team = Team(
                name=name,
                country=str(league.get("country") or "") or None,
                league=str(league.get("name") or "") or None,
                source="api_football",
                external_id=external_id,
            )
            self.session.add(team)
            self.session.flush()
            counters["teams"] += 1
        return team

    def _promote_odds(
        self,
        observations: tuple[SourceObservation, ...],
        matches: dict[str, Match],
        markets: dict[str, Market],
    ) -> int:
        created = 0
        for observation in observations:
            if observation.provider != "api_football":
                continue
            row = observation.values
            fixture = row.get("fixture") if isinstance(row, dict) else None
            if not isinstance(fixture, dict):
                continue
            match = matches.get(str(fixture.get("id")))
            if match is None:
                continue
            for bookmaker in row.get("bookmakers", ()):
                if not isinstance(bookmaker, dict):
                    continue
                bookmaker_name = str(bookmaker.get("name") or "unknown")
                for bet in bookmaker.get("bets", ()):
                    if not isinstance(bet, dict):
                        continue
                    for code, selection, value in _mapped_odds(bet):
                        market = markets[code]
                        exists = self.session.scalar(
                            select(Odd.id).where(
                                Odd.match_id == match.id,
                                Odd.market_id == market.id,
                                Odd.bookmaker == bookmaker_name,
                                Odd.selection == selection,
                                Odd.odd_value == value,
                            )
                        )
                        if exists is None:
                            self.session.add(
                                Odd(
                                    match_id=match.id,
                                    market_id=market.id,
                                    bookmaker=bookmaker_name,
                                    selection=selection,
                                    odd_value=value,
                                    is_closing=False,
                                )
                            )
                            created += 1
        return created

    def _predict(self, match: Match, markets: dict[str, Market]) -> int:
        home = self.session.get(Team, match.home_team_id)
        away = self.session.get(Team, match.away_team_id)
        if home is None or away is None:
            return 0
        home_xg = max(
            Decimal("0.2"),
            Decimal("1.35") + Decimal(str(home.attack_rating - away.defense_rating)) / 50,
        )
        away_xg = max(
            Decimal("0.2"),
            Decimal("1.10") + Decimal(str(away.attack_rating - home.defense_rating)) / 50,
        )
        model = PoissonScoreModel(
            ModelSpecification(
                "operational_poisson",
                self.model_version,
                str(match.competition_id),
                "1x2",
                {},
            )
        )
        forecasts = {
            "match_winner": model.predict(home_xg, away_xg, market="1x2").probabilities,
            "over_2_5_goals": {
                "Over 2.5": model.predict(
                    home_xg, away_xg, market="over_under"
                ).probabilities["over"]
            },
            "under_2_5_goals": {
                "Under 2.5": model.predict(
                    home_xg, away_xg, market="over_under"
                ).probabilities["under"]
            },
            "both_teams_to_score": {
                key.title(): value
                for key, value in model.predict(
                    home_xg, away_xg, market="both_teams_to_score"
                ).probabilities.items()
            },
        }
        forecasts["match_winner"] = {
            {"home": "Home", "draw": "Draw", "away": "Away"}[key]: value
            for key, value in forecasts["match_winner"].items()
        }
        created = 0
        for code, selections in forecasts.items():
            market = markets[code]
            for selection, probability in selections.items():
                exists = self.session.scalar(
                    select(Prediction.id).where(
                        Prediction.match_id == match.id,
                        Prediction.market_id == market.id,
                        Prediction.selection == selection,
                        Prediction.model_version == self.model_version,
                    )
                )
                if exists is not None:
                    continue
                latest_odd = self.session.scalar(
                    select(Odd)
                    .where(
                        Odd.match_id == match.id,
                        Odd.market_id == market.id,
                        Odd.selection == selection,
                    )
                    .order_by(Odd.collected_at.desc())
                )
                implied = (
                    calculate_implied_probability(float(latest_odd.odd_value))
                    if latest_odd is not None
                    else None
                )
                expected = (
                    calculate_expected_value(
                        float(probability),
                        float(latest_odd.odd_value),
                    )
                    if latest_odd is not None
                    else None
                )
                self.session.add(
                    Prediction(
                        match_id=match.id,
                        market_id=market.id,
                        selection=selection,
                        model_version=self.model_version,
                        probability=float(probability),
                        implied_probability=implied,
                        expected_value=expected,
                        confidence=0.55,
                        uqs=0.5,
                        use_score=0.5,
                        confluence=0.5,
                        evidence_level="low",
                        risk_level="moderate",
                    )
                )
                created += 1
        return created


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _mapped_odds(bet: dict[str, Any]) -> tuple[tuple[str, str, Decimal], ...]:
    name = str(bet.get("name") or "").casefold()
    result: list[tuple[str, str, Decimal]] = []
    for item in bet.get("values", ()):
        if not isinstance(item, dict):
            continue
        try:
            odd = Decimal(str(item["odd"]))
        except (KeyError, ArithmeticError):
            continue
        label = str(item.get("value") or "")
        if name == "match winner" and label in {"Home", "Draw", "Away"}:
            result.append(("match_winner", label, odd))
        elif name in {"goals over/under", "over/under"}:
            if label == "Over 2.5":
                result.append(("over_2_5_goals", label, odd))
            elif label == "Under 2.5":
                result.append(("under_2_5_goals", label, odd))
        elif name in {"both teams score", "both teams to score"} and label in {"Yes", "No"}:
            result.append(("both_teams_to_score", label, odd))
    return tuple(result)
