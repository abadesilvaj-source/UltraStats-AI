from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Audit, MatchStatistics
from app.repositories import (
    AuditRepository,
    BetRepository,
    MarketRepository,
    MatchRepository,
    MatchStatisticsRepository,
    PredictionRepository,
)
from app.utils.market_evaluator import evaluate_market

from app.services.bankroll_accounting_service import (
    BankrollAccountingService,
)


class PostMatchService:
    """
    Responsável por registrar resultados oficiais,
    estatísticas, liquidar apostas e criar auditorias.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

        self.match_repository = MatchRepository(session)
        self.statistics_repository = (
            MatchStatisticsRepository(session)
        )
        self.market_repository = MarketRepository(session)
        self.bet_repository = BetRepository(session)
        self.prediction_repository = (
            PredictionRepository(session)
        )
        self.audit_repository = AuditRepository(session)
        self.bankroll_accounting_service = (
            BankrollAccountingService(
                session
            )
        )

    def settle_match(
        self,
        match_external_id: str,
        home_score: int,
        away_score: int,
        source: str,
        corners_home: int | None = None,
        corners_away: int | None = None,
        yellow_cards_home: int | None = None,
        yellow_cards_away: int | None = None,
        red_cards_home: int | None = None,
        red_cards_away: int | None = None,
        shots_home: int | None = None,
        shots_away: int | None = None,
        shots_on_target_home: int | None = None,
        shots_on_target_away: int | None = None,
        offsides_home: int | None = None,
        offsides_away: int | None = None,
        possession_home: float | None = None,
        possession_away: float | None = None,
        xg_home: float | None = None,
        xg_away: float | None = None,
    ) -> dict:
        """
        Fecha uma partida em uma única transação.

        Etapas:

        1. Atualiza o placar.
        2. Registra as estatísticas.
        3. Busca apostas pendentes.
        4. Avalia cada aposta.
        5. Calcula lucro/prejuízo.
        6. Cria auditorias.
        7. Salva tudo de uma vez.
        """

        if home_score < 0 or away_score < 0:
            raise ValueError(
                "Os placares não podem ser negativos."
            )

        match = self.match_repository.find_by_external_id(
            match_external_id
        )

        if not match:
            raise ValueError("Partida não encontrada.")
        
        if match.status == "cancelled":
            raise ValueError(
                "Uma partida cancelada não pode ser liquidada."
            )

        if match.status == "finished":
            raise ValueError(
                "Essa partida já foi encerrada."
            )

        try:
            # ======================================
            # 1. ATUALIZAR A PARTIDA
            # ======================================

            match.home_score = home_score
            match.away_score = away_score
            match.status = "finished"
            match.updated_at = datetime.now()

            self.match_repository.update(match)

            # ======================================
            # 2. REGISTRAR OU ATUALIZAR ESTATÍSTICAS
            # ======================================

            statistics = (
                self.statistics_repository.find_by_match_id(
                    match.id
                )
            )

            if not statistics:
                statistics = MatchStatistics(
                    match_id=match.id,
                )

                self.statistics_repository.create(
                    statistics
                )

            statistics.corners_home = corners_home
            statistics.corners_away = corners_away
            statistics.yellow_cards_home = yellow_cards_home
            statistics.yellow_cards_away = yellow_cards_away
            statistics.red_cards_home = red_cards_home
            statistics.red_cards_away = red_cards_away
            statistics.shots_home = shots_home
            statistics.shots_away = shots_away
            statistics.shots_on_target_home = (
                shots_on_target_home
            )
            statistics.shots_on_target_away = (
                shots_on_target_away
            )
            statistics.offsides_home = offsides_home
            statistics.offsides_away = offsides_away
            statistics.possession_home = possession_home
            statistics.possession_away = possession_away
            statistics.xg_home = xg_home
            statistics.xg_away = xg_away
            statistics.updated_at = datetime.now()

            self.statistics_repository.update(
                statistics
            )

            # ======================================
            # 3. BUSCAR APOSTAS PENDENTES
            # ======================================

            pending_bets = (
                self.bet_repository.list_pending_by_match_id(
                    match.id
                )
            )

            settled_bets = []

            # ======================================
            # 4. LIQUIDAR CADA APOSTA
            # ======================================

            for bet in pending_bets:
                market = self.market_repository.find_by_id(
                    bet.market_id
                )

                if not market:
                    raise ValueError(
                        f"Mercado da aposta {bet.id} "
                        "não encontrado."
                    )

                result = evaluate_market(
                    market_code=market.code,
                    selection=bet.selection,
                    home_score=home_score,
                    away_score=away_score,
                    corners_home=corners_home,
                    corners_away=corners_away,
                    yellow_cards_home=yellow_cards_home,
                    yellow_cards_away=yellow_cards_away,
                    red_cards_home=red_cards_home,
                    red_cards_away=red_cards_away,
                )

                if result == "unsupported":
                    raise ValueError(
                        f"O mercado '{market.code}' "
                        "ainda não possui regra de liquidação."
                    )

                odd_value = float(bet.odd_value)
                stake_units = float(bet.stake_units)

                if result == "won":
                    profit_units = (
                        stake_units * (odd_value - 1)
                    )

                elif result == "lost":
                    profit_units = -stake_units

                elif result == "void":
                    profit_units = 0.0

                else:
                    raise ValueError(
                        f"Resultado de liquidação inválido: "
                        f"{result}"
                    )

                bet.status = "settled"
                bet.result = result
                bet.profit_units = profit_units
                bet.settled_at = datetime.now()

                self.bet_repository.update(bet)
                self.bankroll_accounting_service.settle_bet(
                    bet
                )

                settled_bets.append(bet)

                # ==================================
                # 5. CRIAR OU ATUALIZAR AUDITORIA
                # ==================================

                if bet.prediction_id is not None:
                    prediction = (
                        self.prediction_repository.find_by_id(
                            bet.prediction_id
                        )
                    )

                    if prediction:
                        audit = (
                            self.audit_repository
                            .find_by_prediction_id(
                                prediction.id
                            )
                        )

                        notes = (
                            f"Partida encerrada em "
                            f"{home_score} x {away_score}. "
                            f"Mercado: {market.name}. "
                            f"Seleção: {bet.selection}. "
                            f"Resultado da aposta: {result}. "
                            f"Lucro/prejuízo: "
                            f"{profit_units:.2f}u."
                        )

                        if not audit:
                            audit = Audit(
                                match_id=match.id,
                                prediction_id=prediction.id,
                                source=source,
                                result_status=result,
                                predicted_probability=(
                                    prediction.probability
                                ),
                                calibrated_probability=None,
                                notes=notes,
                            )

                            self.audit_repository.create(audit)

                        else:
                            audit.source = source
                            audit.result_status = result
                            audit.predicted_probability = (
                                prediction.probability
                            )
                            audit.notes = notes
                            audit.audited_at = datetime.now()

                            self.audit_repository.update(audit)

            # ======================================
            # 6. SALVAR TUDO
            # ======================================

            self.session.commit()

            self.session.refresh(match)
            self.session.refresh(statistics)

            for bet in settled_bets:
                self.session.refresh(bet)

            total_profit = sum(
                float(bet.profit_units or 0)
                for bet in settled_bets
            )

            return {
                "match": match,
                "statistics": statistics,
                "settled_bets": settled_bets,
                "total_profit_units": total_profit,
            }

        except Exception:
            self.session.rollback()
            raise

        if not source.strip():
            raise ValueError(
                "A fonte oficial é obrigatória."
            )

        integer_statistics = {
            "Escanteios do mandante": corners_home,
            "Escanteios do visitante": corners_away,
            "Amarelos do mandante": yellow_cards_home,
            "Amarelos do visitante": yellow_cards_away,
            "Vermelhos do mandante": red_cards_home,
            "Vermelhos do visitante": red_cards_away,
            "Finalizações do mandante": shots_home,
            "Finalizações do visitante": shots_away,
            "Finalizações no gol do mandante": (
                shots_on_target_home
            ),
            "Finalizações no gol do visitante": (
                shots_on_target_away
            ),
            "Impedimentos do mandante": offsides_home,
            "Impedimentos do visitante": offsides_away,
        }

        for field_name, value in integer_statistics.items():
            if value is not None and value < 0:
                raise ValueError(
                    f"{field_name} não pode ser negativo."
                )

        if possession_home is not None:
            if possession_home < 0 or possession_home > 100:
                raise ValueError(
                    "A posse do mandante deve estar "
                    "entre 0 e 100."
                )

        if possession_away is not None:
            if possession_away < 0 or possession_away > 100:
                raise ValueError(
                    "A posse do visitante deve estar "
                    "entre 0 e 100."
                )

        if (
            possession_home is not None
            and possession_away is not None
        ):
            possession_total = (
                possession_home
                + possession_away
            )

            if abs(possession_total - 100) > 1:
                raise ValueError(
                    "A soma das posses deve ser "
                    "aproximadamente 100%."
                )

        if xg_home is not None and xg_home < 0:
            raise ValueError(
                "O xG do mandante não pode ser negativo."
            )

        if xg_away is not None and xg_away < 0:
            raise ValueError(
                "O xG do visitante não pode ser negativo."
            )