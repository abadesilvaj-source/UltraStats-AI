from sqlalchemy.orm import Session

from app.repositories import (
    BankrollTransactionRepository,
    BetRepository,
    CompetitionRepository,
    MarketRepository,
    MatchRepository,
    PredictionRepository,
    TeamRepository,
)

from app.services import (
    AnalysisService,
    BankrollService,
    PerformanceService,
    RiskService,
)

from app.services import RiskService

class DashboardService:
    """
    Organiza os dados utilizados pelas páginas
    do Dashboard Pro.

    A interface não acessará diretamente
    os models ou o banco de dados.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

        self.performance_service = (
            PerformanceService(session)
        )

        self.bankroll_service = (
            BankrollService(session)
        )

        self.transaction_repository = (
            BankrollTransactionRepository(
                session
            )
        )

        self.bet_repository = BetRepository(
            session
        )

        self.prediction_repository = (
            PredictionRepository(session)
        )

        self.risk_service = RiskService(
            session
        )

        self.analysis_service = AnalysisService(
            session
        )

        self.match_repository = MatchRepository(
            session
        )

        self.market_repository = MarketRepository(
            session
        )

        self.team_repository = TeamRepository(
            session
        )

        self.competition_repository = (
            CompetitionRepository(session)
        )

    def get_home_data(self) -> dict:
        performance = (
            self.performance_service
            .get_general_summary()
        )

        bankrolls = (
            self.bankroll_service
            .list_bankrolls()
        )

        active_bankroll = next(
            (
                bankroll
                for bankroll in bankrolls
                if bankroll.active
            ),
            None,
        )

        bankroll_data = None

        if active_bankroll:
            unit_value = (
                self.bankroll_service
                .calculate_unit_value(
                    active_bankroll.id
                )
            )

            bankroll_data = {
                "id": active_bankroll.id,
                "name": active_bankroll.name,
                "currency": active_bankroll.currency,
                "initial_balance": float(
                    active_bankroll.initial_balance
                ),
                "current_balance": float(
                    active_bankroll.current_balance
                ),
                "unit_percentage": float(
                    active_bankroll.unit_percentage
                ),
                "unit_value": unit_value,
            }

        bets = self.bet_repository.list_all()

        pending_bets = sum(
            1
            for bet in bets
            if bet.status == "pending"
        )

        official_bets = sum(
            1
            for bet in bets
            if bet.is_official
        )

        return {
            "performance": performance,
            "bankroll": bankroll_data,
            "pending_bets": pending_bets,
            "official_bets": official_bets,
        }

    def get_bankrolls(self) -> list[dict]:
        bankrolls = (
            self.bankroll_service
            .list_bankrolls()
        )

        return [
            {
                "id": bankroll.id,
                "name": bankroll.name,
                "currency": bankroll.currency,
                "initial_balance": float(
                    bankroll.initial_balance
                ),
                "current_balance": float(
                    bankroll.current_balance
                ),
                "unit_percentage": float(
                    bankroll.unit_percentage
                ),
                "active": bankroll.active,
            }
            for bankroll in bankrolls
        ]

    def get_bankroll_details(
        self,
        bankroll_id: int,
    ) -> dict:
        bankroll = (
            self.bankroll_service.get_bankroll(
                bankroll_id
            )
        )

        transactions = (
            self.transaction_repository
            .list_by_bankroll_id(
                bankroll_id
            )
        )

        transaction_rows = [
            {
                "id": transaction.id,
                "date": transaction.created_at,
                "type": (
                    transaction.transaction_type
                ),
                "amount": float(
                    transaction.amount
                ),
                "balance_before": float(
                    transaction.balance_before
                ),
                "balance_after": float(
                    transaction.balance_after
                ),
                "description": (
                    transaction.description
                ),
                "bet_id": transaction.bet_id,
            }
            for transaction in transactions
        ]

        initial_balance = float(
            bankroll.initial_balance
        )

        current_balance = float(
            bankroll.current_balance
        )

        unit_value = (
            self.bankroll_service
            .calculate_unit_value(
                bankroll.id
            )
        )

        peak_balance = initial_balance
        maximum_drawdown = 0.0

        for row in transaction_rows:
            balance = row["balance_after"]

            if balance > peak_balance:
                peak_balance = balance

            if peak_balance > 0:
                drawdown = (
                    (
                        peak_balance
                        - balance
                    )
                    / peak_balance
                    * 100
                )

                maximum_drawdown = max(
                    maximum_drawdown,
                    drawdown,
                )

        current_drawdown = 0.0

        if peak_balance > 0:
            current_drawdown = (
                (
                    peak_balance
                    - current_balance
                )
                / peak_balance
                * 100
            )

        profit = (
            current_balance
            - initial_balance
        )

        profit_percentage = 0.0

        if initial_balance > 0:
            profit_percentage = (
                profit
                / initial_balance
                * 100
            )

        return {
            "bankroll": {
                "id": bankroll.id,
                "name": bankroll.name,
                "currency": bankroll.currency,
                "initial_balance": initial_balance,
                "current_balance": current_balance,
                "unit_percentage": float(
                    bankroll.unit_percentage
                ),
                "unit_value": unit_value,
                "profit": profit,
                "profit_percentage": (
                    profit_percentage
                ),
                "current_drawdown": (
                    current_drawdown
                ),
                "maximum_drawdown": (
                    maximum_drawdown
                ),
            },
            "transactions": transaction_rows,
        }

    def get_performance_data(self) -> dict:
        return {
            "summary": (
                self.performance_service
                .get_general_summary()
            ),
            "markets": (
                self.performance_service
                .get_market_performance()
            ),
            "competitions": (
                self.performance_service
                .get_competition_performance()
            ),
            "timeline": (
                self.performance_service
                .get_profit_timeline()
            ),
        }

    def get_bets(self) -> list[dict]:
        bets = self.bet_repository.list_all()

        return [
            {
                "id": bet.id,
                "match_id": bet.match_id,
                "market_id": bet.market_id,
                "prediction_id": (
                    bet.prediction_id
                ),
                "bankroll_id": (
                    bet.bankroll_id
                ),
                "selection": bet.selection,
                "odd": float(bet.odd_value),
                "stake_units": float(
                    bet.stake_units
                ),
                "stake_amount": (
                    float(bet.stake_amount)
                    if bet.stake_amount
                    is not None
                    else None
                ),
                "payout_amount": (
                    float(bet.payout_amount)
                    if bet.payout_amount
                    is not None
                    else None
                ),
                "status": bet.status,
                "result": bet.result,
                "profit_units": (
                    float(bet.profit_units)
                    if bet.profit_units
                    is not None
                    else None
                ),
                "official": bet.is_official,
                "placed_at": bet.placed_at,
                "settled_at": bet.settled_at,
            }
            for bet in bets
        ]

    def get_predictions(self) -> list[dict]:
        predictions = (
            self.prediction_repository
            .list_all()
        )

        return [
            {
                "id": prediction.id,
                "match_id": (
                    prediction.match_id
                ),
                "market_id": (
                    prediction.market_id
                ),
                "selection": (
                    prediction.selection
                ),
                "model_version": (
                    prediction.model_version
                ),
                "probability": (
                    prediction.probability
                ),
                "implied_probability": (
                    prediction
                    .implied_probability
                ),
                "expected_value": (
                    prediction.expected_value
                ),
                "confidence": (
                    prediction.confidence
                ),
                "uqs": prediction.uqs,
                "use_score": (
                    prediction.use_score
                ),
                "confluence": (
                    prediction.confluence
                ),
                "evidence_level": (
                    prediction.evidence_level
                ),
                "risk_level": (
                    prediction.risk_level
                ),
                "created_at": (
                    prediction.created_at
                ),
            }
            for prediction in predictions
        ]
    
    def simulate_stake(
        self,
        bankroll_id: int,
        probability: float,
        odd_value: float,
        profile_code: str,
    ) -> dict:
        """
        Simula uma recomendação de stake sem criar aposta.

        Nenhuma informação é salva no banco.
        """

        return self.risk_service.recommend_stake(
            bankroll_id=bankroll_id,
            probability=probability,
            odd_value=odd_value,
            profile_code=profile_code,
        )

    def get_risk_summary(
        self,
        bankroll_id: int,
    ) -> dict:
        """
        Retorna um resumo simples do risco
        atual da banca.
        """

        bankroll = self.bankroll_service.get_bankroll(
            bankroll_id
        )

        balance = float(
            bankroll.current_balance
        )

        daily_exposure = (
            self.risk_service.get_daily_exposure(
                bankroll_id
            )
        )

        exposure_percentage = 0.0

        if balance > 0:
            exposure_percentage = (
                daily_exposure
                / balance
                * 100
            )

        return {
            "bankroll_id": bankroll.id,
            "balance": balance,
            "daily_exposure": daily_exposure,
            "exposure_percentage": exposure_percentage,
        }
    
    def create_bankroll(
        self,
        name: str,
        initial_balance: float,
        currency: str,
        unit_percentage: float,
    ) -> dict:
        bankroll = (
            self.bankroll_service.create_bankroll(
                name=name,
                initial_balance=initial_balance,
                currency=currency,
                unit_percentage=unit_percentage,
            )
        )

        return {
            "id": bankroll.id,
            "name": bankroll.name,
            "currency": bankroll.currency,
            "current_balance": float(
                bankroll.current_balance
            ),
        }

    def deposit_to_bankroll(
        self,
        bankroll_id: int,
        amount: float,
        description: str | None,
    ) -> dict:
        transaction = (
            self.bankroll_service.deposit(
                bankroll_id=bankroll_id,
                amount=amount,
                description=description,
            )
        )

        return {
            "transaction_id": transaction.id,
            "amount": float(
                transaction.amount
            ),
            "balance_after": float(
                transaction.balance_after
            ),
        }

    def withdraw_from_bankroll(
        self,
        bankroll_id: int,
        amount: float,
        description: str | None,
    ) -> dict:
        transaction = (
            self.bankroll_service.withdraw(
                bankroll_id=bankroll_id,
                amount=amount,
                description=description,
            )
        )

        return {
            "transaction_id": transaction.id,
            "amount": float(
                transaction.amount
            ),
            "balance_after": float(
                transaction.balance_after
            ),
        }

    def adjust_bankroll(
        self,
        bankroll_id: int,
        amount: float,
        description: str,
    ) -> dict:
        transaction = (
            self.bankroll_service.manual_adjustment(
                bankroll_id=bankroll_id,
                amount=amount,
                description=description,
            )
        )

        return {
            "transaction_id": transaction.id,
            "amount": float(
                transaction.amount
            ),
            "balance_after": float(
                transaction.balance_after
            ),
        }

    def set_bankroll_status(
        self,
        bankroll_id: int,
        active: bool,
    ) -> dict:
        bankroll = (
            self.bankroll_service.set_active_status(
                bankroll_id=bankroll_id,
                active=active,
            )
        )

        return {
            "id": bankroll.id,
            "name": bankroll.name,
            "active": bankroll.active,
        }
    
    def get_betting_form_data(
        self,
    ) -> dict:
        """
        Retorna os dados necessários para
        preencher o formulário de aposta.
        """

        matches = (
            self.match_repository
            .list_available_for_betting()
        )

        markets = (
            self.market_repository
            .list_all()
        )

        bankrolls = (
            self.bankroll_service
            .list_bankrolls()
        )

        match_rows = []

        for match in matches:
            home_team = (
                self.team_repository.find_by_id(
                    match.home_team_id
                )
            )

            away_team = (
                self.team_repository.find_by_id(
                    match.away_team_id
                )
            )

            competition = (
                self.competition_repository
                .find_by_id(
                    match.competition_id
                )
            )

            if not home_team or not away_team:
                continue

            competition_name = (
                competition.name
                if competition
                else "Competição não informada"
            )

            label = (
                f"{home_team.name} x "
                f"{away_team.name} | "
                f"{competition_name} | "
                f"{match.kickoff_at:%d/%m/%Y %H:%M}"
            )

            match_rows.append(
                {
                    "id": match.id,
                    "external_id": (
                        match.external_id
                    ),
                    "label": label,
                    "home_team": home_team.name,
                    "away_team": away_team.name,
                    "competition": competition_name,
                    "kickoff_at": match.kickoff_at,
                    "status": match.status,
                }
            )

        market_rows = [
            {
                "id": market.id,
                "code": market.code,
                "name": market.name,
                "category": market.category,
                "label": (
                    f"{market.name} "
                    f"({market.category})"
                ),
            }
            for market in markets
            if market.active
        ]

        bankroll_rows = [
            {
                "id": bankroll.id,
                "name": bankroll.name,
                "currency": bankroll.currency,
                "current_balance": float(
                    bankroll.current_balance
                ),
                "unit_percentage": float(
                    bankroll.unit_percentage
                ),
                "active": bankroll.active,
                "label": (
                    f"{bankroll.name} | "
                    f"{bankroll.currency} "
                    f"{float(bankroll.current_balance):.2f}"
                ),
            }
            for bankroll in bankrolls
            if bankroll.active
        ]

        return {
            "matches": match_rows,
            "markets": market_rows,
            "bankrolls": bankroll_rows,
        }
    
    def create_managed_bet(
        self,
        bankroll_id: int,
        match_external_id: str,
        market_code: str,
        bookmaker: str,
        selection: str,
        odd_value: float,
        model_probability: float,
        profile_code: str,
        model_version: str,
        confidence: float,
        uqs: float,
        use_score: float,
        confluence: float,
        evidence_level: str,
        risk_level: str,
    ) -> dict:
        """
        Calcula o risco e registra uma aposta oficial.
        """

        recommendation = (
            self.risk_service.recommend_stake(
                bankroll_id=bankroll_id,
                probability=model_probability,
                odd_value=odd_value,
                profile_code=profile_code,
            )
        )

        if not recommendation["approved"]:
            raise ValueError(
                recommendation["reason"]
            )

        odd, prediction, bet = (
            self.analysis_service
            .register_analysis(
                match_external_id=(
                    match_external_id
                ),
                market_code=market_code,
                bookmaker=bookmaker,
                selection=selection,
                odd_value=odd_value,
                model_probability=(
                    model_probability
                ),
                model_version=model_version,
                confidence=confidence,
                uqs=uqs,
                use_score=use_score,
                confluence=confluence,
                evidence_level=evidence_level,
                risk_level=risk_level,
                create_official_bet=True,
                stake_units=(
                    recommendation[
                        "stake_units"
                    ]
                ),
                bankroll_id=bankroll_id,
                stake_amount=(
                    recommendation[
                        "stake_amount"
                    ]
                ),
            )
        )

        if bet is None:
            raise ValueError(
                "A aposta não foi criada."
            )

        return {
            "bet_id": bet.id,
            "odd_id": odd.id,
            "prediction_id": prediction.id,
            "selection": bet.selection,
            "odd": float(bet.odd_value),
            "stake_units": float(
                bet.stake_units
            ),
            "stake_amount": (
                float(bet.stake_amount)
                if bet.stake_amount
                is not None
                else 0.0
            ),
            "expected_value": float(
                prediction.expected_value
                or 0
            ),
            "model_probability": float(
                prediction.probability
            ),
            "implied_probability": float(
                prediction.implied_probability
                or 0
            ),
            "risk_profile": (
                recommendation["profile"]
            ),
        }