from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.competition_catalog import competition_policy
from app.models import Competition, Match, MatchStatistics, Odd


class CompetitionPromotionService:
    """Promove ligas observadas após cobertura suficiente e sustentada.

    Políticas do catálogo nunca são modificadas. Promoções são monotônicas:
    uma queda temporária de cobertura atualiza as métricas, mas não rebaixa uma
    competição já promovida e não interrompe funcionalidades existentes.
    """

    def __init__(self, session: Session, environment=None) -> None:
        self.session = session
        self.environment = environment if environment is not None else os.environ

    def evaluate(self) -> dict[str, object]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        window_days = self._integer("AUTO_CORE_WINDOW_DAYS", 30, minimum=14)
        sustain_days = self._integer("AUTO_CORE_SUSTAIN_DAYS", 7, minimum=0)
        minimum_finished = self._integer(
            "AUTO_CORE_MIN_FINISHED_MATCHES", 20, minimum=1
        )
        minimum_odds = self._integer(
            "AUTO_CORE_MIN_ODDS_MATCHES", 5, minimum=1
        )
        statistics_threshold = self._ratio(
            "AUTO_CORE_STATISTICS_COVERAGE", .90
        )
        odds_threshold = self._ratio("AUTO_CORE_ODDS_COVERAGE", .80)
        cutoff = now - timedelta(days=window_days)
        odds_cutoff = now - timedelta(hours=8)
        odds_end = now + timedelta(days=14)
        candidates = [
            competition
            for competition in self.session.scalars(
                select(Competition).where(Competition.active.is_(True))
            ).all()
            if competition_policy(
                competition.name, competition.country
            ) is None
        ]
        promoted: list[int] = []
        qualified: list[int] = []
        for competition in candidates:
            finished_ids = list(self.session.scalars(
                select(Match.id).where(
                    Match.competition_id == competition.id,
                    Match.status == "finished",
                    Match.kickoff_at >= cutoff,
                    Match.kickoff_at <= now,
                )
            ).all())
            active_ids = list(self.session.scalars(
                select(Match.id).where(
                    Match.competition_id == competition.id,
                    Match.status.in_(("scheduled", "not_started", "in_progress")),
                    Match.kickoff_at >= now - timedelta(hours=3),
                    Match.kickoff_at <= odds_end,
                )
            ).all())
            statistics_count = int(self.session.scalar(
                select(func.count(func.distinct(MatchStatistics.match_id))).where(
                    MatchStatistics.match_id.in_(finished_ids or [-1])
                )
            ) or 0)
            odds_count = int(self.session.scalar(
                select(func.count(func.distinct(Odd.match_id))).where(
                    Odd.match_id.in_(active_ids or [-1]),
                    Odd.collected_at >= odds_cutoff,
                )
            ) or 0)
            statistics_coverage = self._coverage(
                statistics_count, len(finished_ids)
            )
            odds_coverage = self._coverage(odds_count, len(active_ids))
            passes = bool(
                len(finished_ids) >= minimum_finished
                and len(active_ids) >= minimum_odds
                and statistics_coverage >= statistics_threshold
                and odds_coverage >= odds_threshold
            )
            competition.promotion_metrics = {
                "window_days": window_days,
                "finished_matches": len(finished_ids),
                "statistics_matches": statistics_count,
                "statistics_coverage": statistics_coverage,
                "active_matches": len(active_ids),
                "odds_matches": odds_count,
                "odds_coverage": odds_coverage,
                "required": {
                    "finished_matches": minimum_finished,
                    "odds_matches": minimum_odds,
                    "statistics_coverage": statistics_threshold,
                    "odds_coverage": odds_threshold,
                    "sustain_days": sustain_days,
                },
                "qualified": passes,
            }
            competition.promotion_evaluated_at = now
            if competition.auto_core:
                competition.promotion_status = "promoted"
                continue
            if not passes:
                competition.promotion_status = "observation"
                competition.promotion_qualified_since = None
                continue
            if competition.promotion_qualified_since is None:
                competition.promotion_qualified_since = now
            qualified.append(competition.id)
            if now - competition.promotion_qualified_since >= timedelta(
                days=sustain_days
            ):
                competition.auto_core = True
                competition.promotion_status = "promoted"
                promoted.append(competition.id)
            else:
                competition.promotion_status = "candidate"
        self.session.flush()
        return {
            "evaluated": len(candidates),
            "qualified": len(qualified),
            "promoted": len(promoted),
            "promoted_ids": promoted,
        }

    def _integer(self, name: str, default: int, *, minimum: int) -> int:
        return max(minimum, int(self.environment.get(name, str(default))))

    def _ratio(self, name: str, default: float) -> float:
        return min(1.0, max(0.0, float(self.environment.get(name, str(default)))))

    @staticmethod
    def _coverage(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0.0
