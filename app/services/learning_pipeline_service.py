from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Audit, Match, MatchStatistics, Prediction, Team
from app.repositories import MarketRepository
from app.utils.market_evaluator import evaluate_market


class LearningPipelineService:
    """Fecha o ciclo resultado → auditoria → ratings → próxima previsão."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.markets = MarketRepository(session)

    def process(self, match: Match, statistics: MatchStatistics) -> dict:
        audited = self._audit_predictions(match, statistics)
        self._update_team(match.home_team_id, match, statistics, home=True)
        self._update_team(match.away_team_id, match, statistics, home=False)
        self._update_contextual_elo(match)
        return {
            "audited_predictions": audited,
            "ratings_updated": 2,
            "contextual_elo_updated": True,
        }

    def _update_contextual_elo(self, match: Match) -> None:
        home = self.session.get(Team, match.home_team_id)
        away = self.session.get(Team, match.away_team_id)
        if (
            home is None or away is None
            or match.home_score is None or match.away_score is None
        ):
            return
        home_elo = 500 + float(home.power_rating) * 20
        away_elo = 500 + float(away.power_rating) * 20
        expected_home = 1 / (
            1 + 10 ** ((away_elo - (home_elo + 65)) / 400)
        )
        actual_home = (
            1.0 if match.home_score > match.away_score
            else .5 if match.home_score == match.away_score
            else 0.0
        )
        goal_margin = abs(match.home_score - match.away_score)
        multiplier = 1 + min(2, goal_margin) * .15
        delta = 18 * multiplier * (actual_home - expected_home)
        home.power_rating = max(
            1, min(100, (home_elo + delta - 500) / 20)
        )
        away.power_rating = max(
            1, min(100, (away_elo - delta - 500) / 20)
        )

    def _audit_predictions(
        self, match: Match, statistics: MatchStatistics
    ) -> int:
        created = 0
        predictions = self.session.scalars(
            select(Prediction).where(Prediction.match_id == match.id)
        ).all()
        for prediction in predictions:
            exists = self.session.scalar(
                select(Audit.id).where(Audit.prediction_id == prediction.id)
            )
            if exists is not None:
                continue
            market = self.markets.find_by_id(prediction.market_id)
            try:
                result = evaluate_market(
                    market.code,
                    prediction.selection,
                    int(match.home_score or 0),
                    int(match.away_score or 0),
                    statistics.corners_home,
                    statistics.corners_away,
                    statistics.yellow_cards_home,
                    statistics.yellow_cards_away,
                    statistics.red_cards_home,
                    statistics.red_cards_away,
                )
            except ValueError:
                result = "insufficient_data"
            if result == "unsupported":
                continue
            observed = 1.0 if result == "won" else 0.0
            brier = (prediction.probability - observed) ** 2
            calibrated = self._calibrated_probability(prediction)
            self.session.add(
                Audit(
                    match_id=match.id,
                    prediction_id=prediction.id,
                    source="automatic_learning_pipeline",
                    result_status=result,
                    predicted_probability=prediction.probability,
                    calibrated_probability=calibrated,
                    notes=f"Brier={brier:.6f}; modelo={prediction.model_version}",
                    audited_at=datetime.now(),
                )
            )
            created += 1
        return created

    def _calibrated_probability(self, prediction: Prediction) -> float:
        lower = max(0.0, prediction.probability - 0.10)
        upper = min(1.0, prediction.probability + 0.10)
        history = self.session.execute(
            select(Audit.result_status, Audit.predicted_probability)
            .join(Prediction, Prediction.id == Audit.prediction_id)
            .where(
                Prediction.model_version == prediction.model_version,
                Audit.predicted_probability >= lower,
                Audit.predicted_probability <= upper,
                Audit.result_status.in_(("won", "lost")),
            )
            .order_by(Audit.audited_at.desc())
            .limit(250)
        ).all()
        if len(history) < 20:
            return prediction.probability
        wins = sum(status == "won" for status, _ in history)
        # Suavização bayesiana evita saltos com amostras ainda pequenas.
        return (wins + prediction.probability * 20) / (len(history) + 20)

    def _update_team(
        self,
        team_id: int,
        match: Match,
        statistics: MatchStatistics,
        *,
        home: bool,
    ) -> None:
        team = self.session.get(Team, team_id)
        scored = match.home_score if home else match.away_score
        conceded = match.away_score if home else match.home_score
        corners = statistics.corners_home if home else statistics.corners_away
        cards = (
            (statistics.yellow_cards_home or 0) + (statistics.red_cards_home or 0)
            if home
            else (statistics.yellow_cards_away or 0) + (statistics.red_cards_away or 0)
        )
        shots = statistics.shots_on_target_home if home else statistics.shots_on_target_away
        alpha = 0.18
        attack_sample = min(100, 35 + 12 * float(scored or 0) + 4 * float(shots or 0))
        defense_sample = max(0, 75 - 15 * float(conceded or 0))
        team.attack_rating = (1 - alpha) * team.attack_rating + alpha * attack_sample
        team.defense_rating = (1 - alpha) * team.defense_rating + alpha * defense_sample
        team.goal_rating = (team.attack_rating + team.defense_rating) / 2
        if corners is not None:
            team.corner_rating = (1 - alpha) * team.corner_rating + alpha * min(
                100, float(corners) * 10
            )
        team.card_rating = (1 - alpha) * team.card_rating + alpha * min(
            100, float(cards) * 20
        )
        team.power_rating = (
            team.attack_rating + team.defense_rating + team.goal_rating
        ) / 3
