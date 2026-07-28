from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from difflib import SequenceMatcher
from math import exp, factorial
import re
from typing import Any
import unicodedata

from sqlalchemy import func, inspect, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Audit,
    Competition,
    Market,
    Match,
    MatchStatistics,
    Odd,
    Prediction,
    Team,
)
from app.core.football_market_catalog import FOOTBALL_MARKETS
from app.core.competition_catalog import competition_policy
from app.services.post_match_service import PostMatchService
from app.utils.betting_math import (
    calculate_expected_value,
    calculate_implied_probability,
)
from ultrastats_ai.domain.prediction import ModelSpecification, PoissonScoreModel
from ultrastats_ai.infrastructure.providers import DataCapability, SourceObservation
from ultrastats_ai.infrastructure.database.models import RawProviderPayloadRecord
from ultrastats_ai.infrastructure.database.models import IdentityDecisionRecord


MARKETS = tuple(
    (market.code, market.name, market.category)
    for market in FOOTBALL_MARKETS
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
            tuple[str, float, int, int]
        ] | None = None
        self._market_sample_cache: dict[int, int] = {}

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
            if observation.capability is not DataCapability.FIXTURES:
                continue
            match = self._canonical_match(
                observation.provider, observation.external_id
            )
            # Compatibilidade para bancos mínimos/legados: em produção a
            # fusão cria a identidade canônica antes deste pipeline.
            if (
                match is None
                and observation.provider == "api_football"
            ):
                match = self._promote_fixture(
                    observation.values, counters
                )
            if match is not None:
                matches[
                    f"{observation.provider}:{observation.external_id}"
                ] = match

        self.session.flush()
        counters["odds"] += self._promote_odds(odds, matches, markets)
        self.session.flush()
        for match in matches.values():
            if match.status in {"scheduled", "in_progress"}:
                counters["predictions"] += self._predict(match, markets)
        return counters

    def _canonical_match(
        self, provider: str, external_id: str
    ) -> Match | None:
        decision = None
        if inspect(self.session.connection()).has_table(
            IdentityDecisionRecord.__tablename__
        ):
            decision = self.session.scalar(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.provider == provider,
                    IdentityDecisionRecord.external_id
                    == f"match:{external_id}",
                    IdentityDecisionRecord.status == "matched",
                )
            )
        if decision and decision.candidate_id:
            return self.session.get(
                Match,
                int(decision.candidate_id.removeprefix("match:")),
            )
        return self.session.scalar(
            select(Match).where(
                Match.source == provider,
                Match.external_id == external_id,
            )
        )

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
            commit=False,
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
                try:
                    with self.session.begin_nested():
                        market = Market(
                            code=code,
                            name=name,
                            category=category,
                            active=True,
                        )
                        self.session.add(market)
                        self.session.flush()
                    counters["markets"] += 1
                except IntegrityError:
                    market = self.session.scalar(
                        select(Market).where(Market.code == code)
                    )
                    if market is None:
                        raise
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
            policy = competition_policy(
                str(league.get("name") or ""),
                str(league.get("country") or "") or None,
            )
            competition = Competition(
                name=(
                    policy.name if policy
                    else str(league.get("name") or f"League {external_id}")
                ),
                country=(
                    policy.country if policy
                    else str(league.get("country") or "") or None
                ),
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
            match = matches.get(
                f"{observation.provider}:{fixture.get('id')}"
            )
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
        match = self._canonical_match(
            observation.provider, observation.external_id
        )
        try:
            kickoff = datetime.fromisoformat(
                str(row["commence_time"]).replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except (KeyError, ValueError):
            return 0
        home_name, away_name = (
            str(row.get("home_team") or ""),
            str(row.get("away_team") or ""),
        )
        if match is None:
            candidates = self.session.scalars(
                select(Match).where(
                    Match.kickoff_at >= kickoff - timedelta(hours=3),
                    Match.kickoff_at <= kickoff + timedelta(hours=3),
                )
            ).all()
            match = next(
                (
                    candidate
                    for candidate in candidates
                    if self._team_similarity(
                        home_name,
                        self.session.get(
                            Team, candidate.home_team_id
                        ).name,
                    ) >= 0.78
                    and self._team_similarity(
                        away_name,
                        self.session.get(
                            Team, candidate.away_team_id
                        ).name,
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
        competition = self.session.get(Competition, match.competition_id)
        if (
            competition is None
            or competition_policy(
                competition.name, competition.country
            ) is None
        ):
            return 0
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
        # A força global diferencia equipes mesmo quando ataque/defesa ainda
        # têm poucas amostras. O ajuste é simétrico e preserva o mando.
        power_gap = Decimal(str(home.power_rating - away.power_rating))
        home_xg = max(Decimal("0.2"), home_xg + power_gap / Decimal("80"))
        away_xg = max(Decimal("0.2"), away_xg - power_gap / Decimal("80"))
        context = self._match_context(match)
        home_xg = max(
            Decimal("0.2"),
            home_xg * Decimal(str(context["home_attack"]))
            / Decimal(str(context["away_defense"])),
        )
        away_xg = max(
            Decimal("0.2"),
            away_xg * Decimal(str(context["away_attack"]))
            / Decimal(str(context["home_defense"])),
        )
        lineup = self._lineup_context(match)
        evidence_base = self._evidence_base(match, lineup)
        home_xg = max(
            Decimal("0.2"),
            home_xg + Decimal(
                str((lineup["home_continuity"] - 0.70) * 0.12)
            ),
        )
        away_xg = max(
            Decimal("0.2"),
            away_xg + Decimal(
                str((lineup["away_continuity"] - 0.70) * 0.12)
            ),
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
                "Over 8.5": Decimal(str(self._poisson_over(
                    8,
                    max(3.0, (home.corner_rating + away.corner_rating)
                        / 10 * context["tempo"]),
                )))
            },
            "over_9_5_corners": {
                "Over 9.5": Decimal(str(self._poisson_over(
                    9,
                    max(3.0, (home.corner_rating + away.corner_rating)
                        / 10 * context["tempo"]),
                )))
            },
            "over_4_5_cards": {
                "Over 4.5": Decimal(str(self._poisson_over(
                    4,
                    max(1.0, (home.card_rating + away.card_rating)
                        / 20 * context["intensity"]),
                )))
            },
        }
        total_goal_lambda = float(home_xg + away_xg)
        home_goal_lambda = float(home_xg)
        away_goal_lambda = float(away_xg)
        total_corner_lambda = max(
            3.0,
            (home.corner_rating + away.corner_rating)
            / 10 * context["tempo"],
        )
        home_corner_lambda = max(
            1.0, home.corner_rating / 10 * context["tempo"]
        )
        away_corner_lambda = max(
            1.0, away.corner_rating / 10 * context["tempo"]
        )
        total_card_lambda = max(
            1.0,
            (home.card_rating + away.card_rating)
            / 20 * context["intensity"],
        )
        home_card_lambda = max(
            .5, home.card_rating / 20 * context["intensity"]
        )
        away_card_lambda = max(
            .5, away.card_rating / 20 * context["intensity"]
        )
        for value in range(0, 6):
            line = f"{value}_5"
            over = Decimal(str(self._poisson_over(
                value, total_goal_lambda
            )))
            forecasts[f"over_{line}_goals"] = {
                f"Over {value}.5": over
            }
            forecasts[f"under_{line}_goals"] = {
                f"Under {value}.5": Decimal("1") - over
            }
        for side, rate in (
            ("home", home_goal_lambda), ("away", away_goal_lambda)
        ):
            for value in range(0, 4):
                line = f"{value}_5"
                over = Decimal(str(self._poisson_over(value, rate)))
                forecasts[f"{side}_over_{line}_goals"] = {
                    f"Over {value}.5": over
                }
                forecasts[f"{side}_under_{line}_goals"] = {
                    f"Under {value}.5": Decimal("1") - over
                }
        for value in range(5, 14):
            line = f"{value}_5"
            over = Decimal(str(self._poisson_over(
                value, total_corner_lambda
            )))
            forecasts[f"over_{line}_corners"] = {
                f"Over {value}.5": over
            }
            forecasts[f"under_{line}_corners"] = {
                f"Under {value}.5": Decimal("1") - over
            }
        for side, rate in (
            ("home", home_corner_lambda), ("away", away_corner_lambda)
        ):
            for value in range(1, 8):
                line = f"{value}_5"
                over = Decimal(str(self._poisson_over(value, rate)))
                forecasts[f"{side}_over_{line}_corners"] = {
                    f"Over {value}.5": over
                }
                forecasts[f"{side}_under_{line}_corners"] = {
                    f"Under {value}.5": Decimal("1") - over
                }
        for value in range(0, 9):
            line = f"{value}_5"
            over = Decimal(str(self._poisson_over(
                value, total_card_lambda
            )))
            forecasts[f"over_{line}_cards"] = {
                f"Over {value}.5": over
            }
            forecasts[f"under_{line}_cards"] = {
                f"Under {value}.5": Decimal("1") - over
            }
        for side, rate in (
            ("home", home_card_lambda), ("away", away_card_lambda)
        ):
            for value in range(0, 6):
                line = f"{value}_5"
                over = Decimal(str(self._poisson_over(value, rate)))
                forecasts[f"{side}_over_{line}_cards"] = {
                    f"Over {value}.5": over
                }
                forecasts[f"{side}_under_{line}_cards"] = {
                    f"Under {value}.5": Decimal("1") - over
                }
        forecasts["match_winner"] = {
            {"home": "Home", "draw": "Draw", "away": "Away"}[key]: value
            for key, value in forecasts["match_winner"].items()
        }
        winner = forecasts["match_winner"]
        forecasts["double_chance"] = {
            "Home or Draw": winner["Home"] + winner["Draw"],
            "Home or Away": winner["Home"] + winner["Away"],
            "Draw or Away": winner["Draw"] + winner["Away"],
        }
        decisive = max(
            Decimal(".0001"), winner["Home"] + winner["Away"]
        )
        forecasts["draw_no_bet"] = {
            "Home": winner["Home"] / decisive,
            "Away": winner["Away"] / decisive,
        }
        forecasts["home_clean_sheet"] = {
            "Yes": Decimal(str(exp(-away_goal_lambda))),
            "No": Decimal("1") - Decimal(str(exp(-away_goal_lambda))),
        }
        forecasts["away_clean_sheet"] = {
            "Yes": Decimal(str(exp(-home_goal_lambda))),
            "No": Decimal("1") - Decimal(str(exp(-home_goal_lambda))),
        }
        forecasts["goals_odd_even"] = {
            "Even": Decimal(str(
                (1 + exp(-2 * total_goal_lambda)) / 2
            )),
            "Odd": Decimal(str(
                (1 - exp(-2 * total_goal_lambda)) / 2
            )),
        }
        exact_goals = {
            str(goals): Decimal(str(
                exp(-total_goal_lambda)
                * total_goal_lambda ** goals / factorial(goals)
            ))
            for goals in range(0, 6)
        }
        exact_goals["6+"] = max(
            Decimal("0"), Decimal("1") - sum(exact_goals.values())
        )
        forecasts["exact_total_goals"] = exact_goals
        score_probabilities: dict[str, Decimal] = {}
        covered = Decimal("0")
        for home_score in range(0, 5):
            for away_score in range(0, 5):
                probability = Decimal(str(
                    exp(-home_goal_lambda)
                    * home_goal_lambda ** home_score
                    / factorial(home_score)
                    * exp(-away_goal_lambda)
                    * away_goal_lambda ** away_score
                    / factorial(away_score)
                ))
                score_probabilities[f"{home_score}-{away_score}"] = probability
                covered += probability
        score_probabilities["Other"] = max(
            Decimal("0"), Decimal("1") - covered
        )
        forecasts["correct_score"] = score_probabilities
        market_consensus = self._winner_market_consensus(match, markets)
        if market_consensus:
            # Odds de múltiplas casas são uma fonte independente da força
            # relativa. O blend impede que ratings neutros gerem a mesma
            # recomendação para todos os confrontos.
            blended = {
                selection: (
                    Decimal("0.35") * forecasts["match_winner"][selection]
                    + Decimal("0.65") * market_consensus[selection]
                )
                for selection in ("Home", "Draw", "Away")
            }
            total = sum(blended.values())
            forecasts["match_winner"] = {
                selection: value / total
                for selection, value in blended.items()
            }
        existing_predictions = {
            (item.market_id, item.selection): item
            for item in self.session.scalars(
                select(Prediction).where(
                    Prediction.match_id == match.id,
                    Prediction.model_version == self.model_version,
                )
            ).all()
        }
        latest_odds: dict[tuple[int, str], Odd] = {}
        for item in self.session.scalars(
            select(Odd)
            .where(Odd.match_id == match.id)
            .order_by(Odd.collected_at.desc())
        ).all():
            latest_odds.setdefault(
                (item.market_id, item.selection), item
            )
        created = 0
        for code, selections in forecasts.items():
            market = markets[code]
            evidence = self._market_evidence(
                match,
                market,
                evidence_base,
            )
            for selection, probability in selections.items():
                calibrated_probability = self._calibrate_probability(
                    float(probability), market.id, match.competition_id
                )
                existing = existing_predictions.get(
                    (market.id, selection)
                )
                latest_odd = latest_odds.get((market.id, selection))
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
                lineup_coverage = int(lineup["coverage"])
                confirmed_lineups = int(lineup["confirmed"])
                continuity = (
                    lineup["home_continuity"]
                    + lineup["away_continuity"]
                ) / 2
                evidence_ratio = float(evidence["score"]) / 10
                prediction = existing or Prediction(
                        match_id=match.id,
                        market_id=market.id,
                        selection=selection,
                        model_version=self.model_version,
                    )
                prediction.probability = calibrated_probability
                prediction.implied_probability = implied
                prediction.expected_value = expected
                prediction.confidence = min(
                    0.90,
                    0.42
                    + (0.30 * evidence_ratio)
                    + (0.04 * confirmed_lineups)
                    + (0.04 * continuity),
                )
                prediction.uqs = min(
                    0.88,
                    0.40 + (0.36 * evidence_ratio)
                    + (0.04 * confirmed_lineups),
                )
                prediction.use_score = min(
                    0.88, 0.40 + (0.40 * evidence_ratio)
                )
                prediction.confluence = min(
                    0.90,
                    0.40 + (0.34 * evidence_ratio)
                    + (0.04 * lineup_coverage)
                    + (0.04 * continuity),
                )
                prediction.evidence_level = str(evidence["level"])
                prediction.risk_level = (
                    "low" if evidence["level"] == "high"
                    else "moderate" if evidence["level"] == "medium"
                    else "high"
                )
                if existing is None:
                    self.session.add(prediction)
                    existing_predictions[
                        (market.id, selection)
                    ] = prediction
                    created += 1
        return created

    def _evidence_base(
        self,
        match: Match,
        lineup: dict[str, float | int],
    ) -> dict[str, int]:
        """Mede evidência observável sem privilegiar um provedor."""
        histories = []
        for team_id in (match.home_team_id, match.away_team_id):
            histories.append(int(self.session.scalar(
                select(func.count())
                .select_from(Match)
                .where(
                    Match.status == "finished",
                    Match.kickoff_at < match.kickoff_at,
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id,
                    ),
                    Match.home_score.is_not(None),
                    Match.away_score.is_not(None),
                )
            ) or 0))
        detailed = int(self.session.scalar(
            select(func.count())
            .select_from(MatchStatistics)
            .join(Match, Match.id == MatchStatistics.match_id)
            .where(
                Match.kickoff_at < match.kickoff_at,
                or_(
                    Match.home_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                    Match.away_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                ),
            )
        ) or 0)
        bookmakers = int(self.session.scalar(
            select(func.count(func.distinct(Odd.bookmaker)))
            .where(Odd.match_id == match.id)
        ) or 0)
        return {
            "team_history": min(histories) if histories else 0,
            "detailed_history": detailed,
            "bookmakers": bookmakers,
            "lineups": int(lineup["coverage"]),
            "confirmed_lineups": int(lineup["confirmed"]),
        }

    def _market_evidence(
        self,
        match: Match,
        market: Market,
        base: dict[str, int],
    ) -> dict[str, int | str]:
        if market.id not in self._market_sample_cache:
            self._market_sample_cache[market.id] = int(
                self.session.scalar(
                    select(func.count(Audit.id))
                    .join(
                        Prediction,
                        Prediction.id == Audit.prediction_id,
                    )
                    .where(
                        Prediction.market_id == market.id,
                        Audit.result_status.in_(("won", "lost")),
                    )
                ) or 0
            )
        samples = self._market_sample_cache[market.id]
        sample_points = 3 if samples >= 100 else 2 if samples >= 50 else 1 if samples >= 20 else 0
        history = base["team_history"]
        history_points = 2 if history >= 10 else 1 if history >= 5 else 0
        details = base["detailed_history"]
        detail_points = 2 if details >= 10 else 1 if details >= 3 else 0
        price_points = 2 if base["bookmakers"] >= 3 else 1 if base["bookmakers"] else 0
        lineup_points = (
            2 if base["confirmed_lineups"] == 2
            else 1 if base["lineups"] == 2
            else 0
        )
        score = min(
            10,
            sample_points + history_points + detail_points
            + price_points + lineup_points,
        )
        level = "high" if score >= 8 else "medium" if score >= 4 else "low"
        return {
            "level": level,
            "score": score,
            "market_samples": samples,
        }

    def _match_context(self, match: Match) -> dict[str, float]:
        rows = self.session.scalars(
            select(Match).where(
                Match.status == "finished",
                Match.kickoff_at < match.kickoff_at,
                or_(
                    Match.home_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                    Match.away_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                ),
            ).order_by(Match.kickoff_at.desc()).limit(40)
        ).all()

        def profile(team_id: int) -> tuple[float, float, float]:
            scored = conceded = weights = 0.0
            last_at = None
            for index, row in enumerate(
                item for item in rows
                if team_id in (item.home_team_id, item.away_team_id)
                and item.home_score is not None
                and item.away_score is not None
            ):
                is_home = row.home_team_id == team_id
                opponent = self.session.get(
                    Team,
                    row.away_team_id if is_home else row.home_team_id,
                )
                opponent_factor = (
                    max(.75, min(1.25, float(opponent.power_rating) / 50))
                    if opponent else 1.0
                )
                weight = exp(-index / 8) * opponent_factor
                scored += float(
                    row.home_score if is_home else row.away_score
                ) * weight
                conceded += float(
                    row.away_score if is_home else row.home_score
                ) * weight
                weights += weight
                last_at = last_at or row.kickoff_at
            if not weights:
                return 1.0, 1.0, 7.0
            match_at = self._naive_utc(match.kickoff_at)
            previous_at = self._naive_utc(last_at)
            rest = max(
                2.0,
                (match_at - previous_at).total_seconds() / 86400,
            )
            return (
                max(.65, min(1.45, scored / weights / 1.35)),
                max(.65, min(1.45, conceded / weights / 1.35)),
                rest,
            )

        home_attack, home_defense, home_rest = profile(match.home_team_id)
        away_attack, away_defense, away_rest = profile(match.away_team_id)
        if home_rest < 4:
            home_attack *= .94
        if away_rest < 4:
            away_attack *= .94
        return {
            "home_attack": home_attack,
            "home_defense": home_defense,
            "away_attack": away_attack,
            "away_defense": away_defense,
            "tempo": max(.80, min(1.20, (home_attack + away_attack) / 2)),
            "intensity": max(
                .85, min(1.20, 1 + abs(home_attack - away_attack) * .15)
            ),
        }

    @staticmethod
    def _naive_utc(value: datetime) -> datetime:
        """Normaliza timestamps mistos antes de calcular intervalos."""
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _poisson_over(line: int, expected: float) -> float:
        below = sum(
            exp(-expected) * expected ** value / factorial(value)
            for value in range(line + 1)
        )
        return max(.02, min(.98, 1 - below))

    def _winner_market_consensus(
        self,
        match: Match,
        markets: dict[str, Market],
    ) -> dict[str, Decimal] | None:
        rows = self.session.scalars(
            select(Odd).where(
                Odd.match_id == match.id,
                Odd.market_id == markets["match_winner"].id,
                Odd.selection.in_(("Home", "Draw", "Away")),
            )
        ).all()
        prices: dict[str, list[Decimal]] = {
            "Home": [], "Draw": [], "Away": []
        }
        for row in rows:
            value = Decimal(str(row.odd_value))
            if value > 1:
                prices[row.selection].append(value)
        if not all(prices.values()):
            return None
        implied = {
            selection: sum(
                (Decimal("1") / value for value in values),
                Decimal("0"),
            ) / len(values)
            for selection, values in prices.items()
        }
        total = sum(implied.values())
        return {
            selection: value / total
            for selection, value in implied.items()
        }

    def _calibrate_probability(
        self,
        probability: float,
        market_id: int | None = None,
        competition_id: int | None = None,
    ) -> float:
        if self._calibration_history is None:
            self._calibration_history = [
                (status, float(predicted or 0), historical_market, competition)
                for status, predicted, historical_market, competition
                in self.session.execute(
                    select(
                        Audit.result_status,
                        Audit.predicted_probability,
                        Prediction.market_id,
                        Match.competition_id,
                    )
                    .join(
                        Prediction,
                        Prediction.id == Audit.prediction_id,
                    )
                    .join(Match, Match.id == Prediction.match_id)
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
            for status, predicted, historical_market, competition
            in self._calibration_history
            if abs(predicted - probability) <= 0.10
            and (market_id is None or historical_market == market_id)
            and (
                competition_id is None or competition == competition_id
            )
        ]
        if len(nearby) < 20 and market_id is not None:
            nearby = [
                status
                for status, predicted, historical_market, _
                in self._calibration_history
                if historical_market == market_id
                and abs(predicted - probability) <= .12
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
        return int(self._lineup_context(match)["coverage"])

    def _lineup_context(self, match: Match) -> dict[str, float | int]:
        connection = self.session.connection()
        if not inspect(connection).has_table(
            RawProviderPayloadRecord.__tablename__
        ):
            return self._empty_lineup_context()
        provider_ids: dict[str, str] = {}
        if match.source and match.external_id:
            external_id = str(match.external_id)
            if match.source == "data_fusion" and ":" in external_id:
                provider, external_id = external_id.split(":", 1)
                provider_ids[provider] = external_id
            else:
                provider_ids[str(match.source)] = external_id
        for decision in self.session.scalars(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.candidate_id == f"match:{match.id}",
                IdentityDecisionRecord.status == "matched",
            )
        ).all():
            provider_ids[decision.provider] = (
                decision.external_id.removeprefix("match:")
            )
        rows: list[RawProviderPayloadRecord] = []
        for provider, external_id in provider_ids.items():
            rows.extend(self.session.scalars(
                select(RawProviderPayloadRecord)
                .where(
                    RawProviderPayloadRecord.provider == provider,
                    RawProviderPayloadRecord.resource == "lineups",
                    RawProviderPayloadRecord.external_id.like(
                        f"{external_id}%"
                    ),
                )
                .order_by(RawProviderPayloadRecord.collected_at.desc())
            ).all())
        current: dict[
            tuple[str, str],
            tuple[set[str], bool],
        ] = {}
        for row in rows:
            for team_id, starters in self._lineup_teams(
                row.provider, row.payload
            ).items():
                key = (row.provider, team_id)
                if key not in current:
                    current[key] = (starters, len(starters) >= 11)
        continuities: list[float] = []
        for (provider, team_id), (starters, _) in current.items():
            history = self.session.scalars(
                select(RawProviderPayloadRecord)
                .where(
                    RawProviderPayloadRecord.provider == provider,
                    RawProviderPayloadRecord.resource == "lineups",
                )
                .order_by(RawProviderPayloadRecord.collected_at.desc())
                .limit(200)
            ).all()
            previous_starters = next(
                (
                    teams[team_id]
                    for item in history
                    if (
                        teams := self._lineup_teams(
                            item.provider, item.payload
                        )
                    )
                    and team_id in teams
                    and teams[team_id] != starters
                ),
                set(),
            )
            continuities.append(
                len(starters.intersection(previous_starters))
                / max(1, len(starters))
                if previous_starters else 0.70
            )
        while len(continuities) < 2:
            continuities.append(0.70)
        return {
            "coverage": min(2, len(current)),
            "confirmed": min(
                2, sum(item[1] for item in current.values())
            ),
            "home_continuity": continuities[0],
            "away_continuity": continuities[1],
        }

    @staticmethod
    def _lineup_teams(
        provider: str,
        payload: dict[str, Any],
    ) -> dict[str, set[str]]:
        if provider == "api_football":
            team_id = str(payload.get("team", {}).get("id") or "")
            starters = {
                str(item.get("player", {}).get("id"))
                for item in payload.get("startXI", ())
                if item.get("player", {}).get("id") is not None
            }
            return {team_id: starters} if team_id and starters else {}
        grouped: dict[str, set[str]] = {}
        for item in payload.get("lineups", ()) or ():
            if not isinstance(item, dict):
                continue
            team = item.get("team") or {}
            player = item.get("player") or {}
            team_id = str(
                item.get("team_id")
                or item.get("participant_id")
                or (team.get("id") if isinstance(team, dict) else "")
                or ""
            )
            player_id = str(
                item.get("player_id")
                or (player.get("id") if isinstance(player, dict) else "")
                or ""
            )
            if team_id and player_id:
                grouped.setdefault(team_id, set()).add(player_id)
        return grouped

    @staticmethod
    def _empty_lineup_context() -> dict[str, float | int]:
        return {
            "coverage": 0,
            "confirmed": 0,
            "home_continuity": 0.70,
            "away_continuity": 0.70,
        }


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
