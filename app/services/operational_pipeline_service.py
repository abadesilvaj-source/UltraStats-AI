from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from difflib import SequenceMatcher
import re
from typing import Any
import unicodedata

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import (
    Audit,
    Competition,
    Market,
    Match,
    Odd,
    Prediction,
    Team,
)
from app.services.post_match_service import PostMatchService
from app.utils.betting_math import (
    calculate_expected_value,
    calculate_implied_probability,
)
from ultrastats_ai.domain.prediction import ModelSpecification, PoissonScoreModel
from ultrastats_ai.infrastructure.providers import DataCapability, SourceObservation
from ultrastats_ai.infrastructure.database.models import RawProviderPayloadRecord


MARKETS = (
    ("match_winner", "Resultado da Partida", "result"),
    ("over_2_5_goals", "Mais de 2.5 Gols", "goals"),
    ("under_2_5_goals", "Menos de 2.5 Gols", "goals"),
    ("under_3_5_goals", "Menos de 3.5 Gols", "goals"),
    ("both_teams_to_score", "Ambas as Equipes Marcam", "goals"),
    ("over_8_5_corners", "Mais de 8.5 Escanteios", "corners"),
    ("over_9_5_corners", "Mais de 9.5 Escanteios", "corners"),
    ("over_4_5_cards", "Mais de 4.5 Cartões", "cards"),
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
        self._calibration_history: list[
            tuple[str, float]
        ] | None = None

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

    def process_post_match_statistics(
        self,
        fixture: SourceObservation,
        statistics: tuple[SourceObservation, ...],
    ) -> dict[str, int]:
        """Persiste estatísticas finais e liquida apostas da partida."""
        row = fixture.values
        fixture_data = row.get("fixture", {})
        teams = row.get("teams", {})
        goals = row.get("goals", {})
        external_id = str(fixture_data.get("id", "")).strip()
        home = teams.get("home", {})
        away = teams.get("away", {})
        if (
            not external_id
            or goals.get("home") is None
            or goals.get("away") is None
        ):
            return {"statistics": 0, "settled_bets": 0}

        by_team = {
            str(item.values.get("team", {}).get("id")): _statistics_values(
                item.values
            )
            for item in statistics
            if isinstance(item.values, dict)
        }
        home_stats = by_team.get(str(home.get("id")), {})
        away_stats = by_team.get(str(away.get("id")), {})
        if not home_stats and not away_stats:
            return {"statistics": 0, "settled_bets": 0}

        result = PostMatchService(self.session).settle_match(
            match_external_id=external_id,
            home_score=int(goals["home"]),
            away_score=int(goals["away"]),
            source="api_football",
            corners_home=_integer_stat(home_stats, "Corner Kicks"),
            corners_away=_integer_stat(away_stats, "Corner Kicks"),
            yellow_cards_home=_integer_stat(home_stats, "Yellow Cards"),
            yellow_cards_away=_integer_stat(away_stats, "Yellow Cards"),
            red_cards_home=_integer_stat(home_stats, "Red Cards"),
            red_cards_away=_integer_stat(away_stats, "Red Cards"),
            shots_home=_integer_stat(home_stats, "Total Shots"),
            shots_away=_integer_stat(away_stats, "Total Shots"),
            shots_on_target_home=_integer_stat(home_stats, "Shots on Goal"),
            shots_on_target_away=_integer_stat(away_stats, "Shots on Goal"),
            offsides_home=_integer_stat(home_stats, "Offsides"),
            offsides_away=_integer_stat(away_stats, "Offsides"),
            possession_home=_percentage_stat(home_stats, "Ball Possession"),
            possession_away=_percentage_stat(away_stats, "Ball Possession"),
            xg_home=_float_stat(home_stats, "expected_goals"),
            xg_away=_float_stat(away_stats, "expected_goals"),
        )
        return {
            "statistics": 1,
            "settled_bets": len(result["settled_bets"]),
        }

    def refresh_all_predictions(self) -> int:
        counters = {"markets": 0}
        markets = self._ensure_markets(counters)
        matches = self.session.scalars(
            select(Match).where(
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= (
                    datetime.now(timezone.utc).replace(tzinfo=None)
                    - timedelta(hours=6)
                ),
                Match.kickoff_at <= (
                    datetime.now(timezone.utc).replace(tzinfo=None)
                    + timedelta(days=14)
                ),
            )
        ).all()
        return sum(self._predict(match, markets) for match in matches)

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
            if observation.provider == "the_odds_api":
                created += self._promote_the_odds_api(
                    observation, markets
                )
                continue
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

    def _promote_the_odds_api(
        self,
        observation: SourceObservation,
        markets: dict[str, Market],
    ) -> int:
        row = observation.values
        try:
            kickoff = datetime.fromisoformat(
                str(row["commence_time"]).replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except (KeyError, ValueError):
            return 0
        candidates = self.session.scalars(
            select(Match).where(
                Match.kickoff_at >= kickoff - timedelta(hours=3),
                Match.kickoff_at <= kickoff + timedelta(hours=3),
            )
        ).all()
        home_name, away_name = (
            str(row.get("home_team") or ""),
            str(row.get("away_team") or ""),
        )
        match = next(
            (
                candidate
                for candidate in candidates
                if self._team_similarity(
                    home_name,
                    self.session.get(Team, candidate.home_team_id).name,
                ) >= 0.78
                and self._team_similarity(
                    away_name,
                    self.session.get(Team, candidate.away_team_id).name,
                ) >= 0.78
            ),
            None,
        )
        if match is None:
            return 0
        created = 0
        for bookmaker in row.get("bookmakers") or []:
            if not isinstance(bookmaker, dict):
                continue
            bookmaker_name = str(
                bookmaker.get("title") or bookmaker.get("key") or "unknown"
            )
            for market_payload in bookmaker.get("markets") or []:
                for code, selection, value in _mapped_external_odds(
                    market_payload, home_name, away_name
                ):
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

    @staticmethod
    def _team_similarity(left: str, right: str) -> float:
        def normalize(value: str) -> str:
            plain = unicodedata.normalize("NFKD", value).encode(
                "ascii", "ignore"
            ).decode().casefold()
            return re.sub(
                r"\b(fc|cf|sc|ac|club|de|the)\b|[^a-z0-9]",
                "",
                plain,
            )

        return SequenceMatcher(
            None, normalize(left), normalize(right)
        ).ratio()

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
            "under_3_5_goals": {
                "Under 3.5": min(
                    Decimal("0.92"),
                    model.predict(
                        home_xg, away_xg, market="over_under"
                    ).probabilities["under"] + Decimal(".15"),
                )
            },
            "both_teams_to_score": {
                key.title(): value
                for key, value in model.predict(
                    home_xg, away_xg, market="both_teams_to_score"
                ).probabilities.items()
            },
            "over_8_5_corners": {
                "Over 8.5": Decimal(
                    str(min(0.82, max(0.18, (
                        home.corner_rating + away.corner_rating
                    ) / 200)))
                )
            },
            "over_9_5_corners": {
                "Over 9.5": Decimal(
                    str(min(0.76, max(0.14, (
                        home.corner_rating + away.corner_rating
                    ) / 220)))
                )
            },
            "over_4_5_cards": {
                "Over 4.5": Decimal(
                    str(min(0.82, max(0.18, (
                        home.card_rating + away.card_rating
                    ) / 200)))
                )
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
                calibrated_probability = self._calibrate_probability(
                    float(probability)
                )
                existing = self.session.scalar(
                    select(Prediction).where(
                        Prediction.match_id == match.id,
                        Prediction.market_id == market.id,
                        Prediction.selection == selection,
                        Prediction.model_version == self.model_version,
                    )
                )
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
                        calibrated_probability,
                        float(latest_odd.odd_value),
                    )
                    if latest_odd is not None
                    else None
                )
                lineup_coverage = self._lineup_coverage(match)
                prediction = existing or Prediction(
                        match_id=match.id,
                        market_id=market.id,
                        selection=selection,
                        model_version=self.model_version,
                    )
                prediction.probability = calibrated_probability
                prediction.implied_probability = implied
                prediction.expected_value = expected
                prediction.confidence = 0.55 + (0.05 * lineup_coverage)
                prediction.uqs = 0.5 + (0.05 * lineup_coverage)
                prediction.use_score = 0.5
                prediction.confluence = 0.5 + (0.05 * lineup_coverage)
                prediction.evidence_level = (
                    "medium" if lineup_coverage == 2 else "low"
                )
                prediction.risk_level = (
                    "moderate" if lineup_coverage == 2 else "high"
                )
                if existing is None:
                    self.session.add(prediction)
                    created += 1
        return created

    def _calibrate_probability(self, probability: float) -> float:
        if self._calibration_history is None:
            self._calibration_history = [
                (status, float(predicted or 0))
                for status, predicted in self.session.execute(
                    select(
                        Audit.result_status,
                        Audit.predicted_probability,
                    )
                    .join(
                        Prediction,
                        Prediction.id == Audit.prediction_id,
                    )
                    .where(
                        Prediction.model_version
                        == self.model_version,
                        Audit.result_status.in_(("won", "lost")),
                    )
                    .order_by(Audit.audited_at.desc())
                    .limit(1000)
                ).all()
            ]
        nearby = [
            status
            for status, predicted in self._calibration_history
            if abs(predicted - probability) <= 0.10
        ]
        if len(nearby) < 20:
            return probability
        observed = sum(
            status == "won" for status in nearby
        ) / len(nearby)
        return (
            observed * len(nearby) + probability * 20
        ) / (len(nearby) + 20)

    def _lineup_coverage(self, match: Match) -> int:
        if not match.external_id:
            return 0
        connection = self.session.connection()
        if not inspect(connection).has_table(
            RawProviderPayloadRecord.__tablename__
        ):
            return 0
        team_ids = self.session.scalars(
            select(RawProviderPayloadRecord.external_id)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "lineups",
                RawProviderPayloadRecord.external_id.like(
                    f"{match.external_id}:%"
                ),
            )
            .distinct()
        ).all()
        return min(2, len(team_ids))


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _statistics_values(row: dict[str, Any]) -> dict[str, Any]:
    return {
        str(item.get("type")): item.get("value")
        for item in row.get("statistics", ())
        if isinstance(item, dict) and item.get("type")
    }


def _integer_stat(values: dict[str, Any], key: str) -> int | None:
    value = values.get(key)
    if value in (None, ""):
        return None
    try:
        return int(float(str(value).rstrip("%")))
    except ValueError:
        return None


def _float_stat(values: dict[str, Any], key: str) -> float | None:
    value = values.get(key)
    if value in (None, ""):
        return None
    try:
        return float(str(value).rstrip("%"))
    except ValueError:
        return None


def _percentage_stat(values: dict[str, Any], key: str) -> float | None:
    return _float_stat(values, key)


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
            elif label == "Under 3.5":
                result.append(("under_3_5_goals", label, odd))
        elif name in {"both teams score", "both teams to score"} and label in {"Yes", "No"}:
            result.append(("both_teams_to_score", label, odd))
        elif "corners" in name and label == "Over 8.5":
            result.append(("over_8_5_corners", label, odd))
        elif "corners" in name and label == "Over 9.5":
            result.append(("over_9_5_corners", label, odd))
        elif "cards" in name and label == "Over 4.5":
            result.append(("over_4_5_cards", label, odd))
    return tuple(result)


def _mapped_external_odds(
    market: dict[str, Any],
    home_name: str,
    away_name: str,
) -> tuple[tuple[str, str, Decimal], ...]:
    key = str(market.get("key") or "")
    result: list[tuple[str, str, Decimal]] = []
    for outcome in market.get("outcomes") or []:
        if not isinstance(outcome, dict):
            continue
        try:
            odd = Decimal(str(outcome["price"]))
        except (KeyError, ArithmeticError):
            continue
        name = str(outcome.get("name") or "")
        point = outcome.get("point")
        if key == "h2h":
            selection = (
                "Home" if name == home_name
                else "Away" if name == away_name
                else "Draw" if name.casefold() == "draw"
                else None
            )
            if selection:
                result.append(("match_winner", selection, odd))
        elif key == "totals" and point in (2.5, 3.5):
            label = f"{name.title()} {point}"
            mapping = {
                "Over 2.5": "over_2_5_goals",
                "Under 2.5": "under_2_5_goals",
                "Under 3.5": "under_3_5_goals",
            }
            if label in mapping:
                result.append((mapping[label], label, odd))
    return tuple(result)
