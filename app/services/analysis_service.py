from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Bet, Odd, Prediction
from app.repositories import (
    BetRepository,
    MarketRepository,
    MatchRepository,
    OddRepository,
    PredictionRepository,
)
from app.utils.betting_math import (
    calculate_expected_value,
    calculate_implied_probability,
    validate_odd,
    validate_probability,
)


class AnalysisService:
    """
    Registra odds, previsões e apostas
    produzidas pelo UltraStats AI.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

        self.match_repository = MatchRepository(session)
        self.market_repository = MarketRepository(session)
        self.odd_repository = OddRepository(session)
        self.prediction_repository = PredictionRepository(session)
        self.bet_repository = BetRepository(session)

    def register_analysis(
        self,
        match_external_id: str,
        market_code: str,
        bookmaker: str,
        selection: str,
        odd_value: float,
        model_probability: float,
        model_version: str,
        confidence: float,
        uqs: float,
        use_score: float,
        confluence: float,
        evidence_level: str,
        risk_level: str,
        create_official_bet: bool = False,
        stake_units: float = 1.0,
    ) -> tuple[Odd, Prediction, Bet | None]:
        """Registra uma análise completa em uma única transação."""

        validate_odd(odd_value)
        validate_probability(model_probability)

        if stake_units <= 0:
            raise ValueError("A stake deve ser maior que zero.")

        match = self.match_repository.find_by_external_id(
            match_external_id
        )

        if not match:
            raise ValueError("Partida não encontrada.")

        market = self.market_repository.find_by_code(
            market_code
        )

        if not market:
            raise ValueError(
                f"Mercado '{market_code}' não encontrado."
            )

        implied_probability = calculate_implied_probability(
            odd_value
        )

        expected_value = calculate_expected_value(
            model_probability,
            odd_value,
        )

        try:
            odd = Odd(
                match_id=match.id,
                market_id=market.id,
                bookmaker=bookmaker,
                selection=selection,
                odd_value=Decimal(str(odd_value)),
                is_closing=False,
            )

            self.odd_repository.create(odd)

            prediction = Prediction(
                match_id=match.id,
                market_id=market.id,
                selection=selection,
                model_version=model_version,
                probability=model_probability,
                implied_probability=implied_probability,
                expected_value=expected_value,
                confidence=confidence,
                uqs=uqs,
                use_score=use_score,
                confluence=confluence,
                evidence_level=evidence_level,
                risk_level=risk_level,
            )

            self.prediction_repository.create(prediction)

            bet = None

            if create_official_bet:
                if expected_value <= 0:
                    raise ValueError(
                        "Aposta oficial rejeitada: EV não é positivo."
                    )

                bet = Bet(
                    prediction_id=prediction.id,
                    match_id=match.id,
                    market_id=market.id,
                    selection=selection,
                    odd_value=Decimal(str(odd_value)),
                    stake_units=stake_units,
                    status="pending",
                    result=None,
                    profit_units=None,
                    is_official=True,
                )

                self.bet_repository.create(bet)

            self.session.commit()

            self.session.refresh(odd)
            self.session.refresh(prediction)

            if bet:
                self.session.refresh(bet)

            return odd, prediction, bet

        except Exception:
            self.session.rollback()
            raise