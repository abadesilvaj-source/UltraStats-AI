from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Bankroll,
    BankrollTransaction,
    BetLeg,
    BetSlip,
    Market,
    Match,
    Odd,
    Prediction,
)
from app.utils.market_evaluator import evaluate_market


class BetSlipService:
    """Registra e liquida bilhetes simples e múltiplos."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def analyze(self, payload: dict) -> dict[str, object]:
        items = payload.get("legs") or []
        if not 1 <= len(items) <= 20:
            raise ValueError("O bilhete deve conter entre 1 e 20 seleções.")
        combined_odds = Decimal("1")
        joint_probability = 1.0
        matches: dict[int, int] = {}
        missing_predictions = 0
        for item in items:
            match_id = int(item["match_id"])
            market_id = int(item["market_id"])
            selection = str(item["selection"]).strip()
            odd = self.session.scalar(
                select(Odd)
                .where(
                    Odd.match_id == match_id,
                    Odd.market_id == market_id,
                    Odd.selection == selection,
                )
                .order_by(Odd.collected_at.desc())
            )
            if odd is None:
                raise ValueError("Odd atual não encontrada.")
            prediction = self.session.scalar(
                select(Prediction)
                .where(
                    Prediction.match_id == match_id,
                    Prediction.market_id == market_id,
                    Prediction.selection == selection,
                )
                .order_by(Prediction.created_at.desc())
            )
            combined_odds *= Decimal(str(odd.odd_value))
            if prediction is None:
                missing_predictions += 1
                joint_probability *= 1 / float(odd.odd_value)
            else:
                joint_probability *= prediction.probability
            matches[match_id] = matches.get(match_id, 0) + 1
        correlated_pairs = sum(
            max(0, amount - 1) for amount in matches.values()
        )
        adjusted_probability = joint_probability * (
            0.85 ** correlated_pairs
        )
        expected_value = (
            adjusted_probability * float(combined_odds) - 1
        )
        warnings = []
        if correlated_pairs:
            warnings.append("correlated_legs")
        if missing_predictions:
            warnings.append("missing_predictions")
        if len(items) > 5:
            warnings.append("high_leg_count")
        return {
            "legs": len(items),
            "combined_odds": float(combined_odds),
            "joint_probability": joint_probability,
            "correlation_adjusted_probability":
                adjusted_probability,
            "expected_value": expected_value,
            "correlated_pairs": correlated_pairs,
            "recommended_max_bankroll_percentage": (
                0.5 if correlated_pairs or len(items) > 5 else 1.0
            ),
            "warnings": warnings,
            "approved": expected_value >= 0.02
            and missing_predictions == 0,
        }

    def create(self, payload: dict) -> BetSlip:
        items = payload.get("legs") or []
        if not 1 <= len(items) <= 20:
            raise ValueError("O bilhete deve conter entre 1 e 20 seleções.")
        bankroll = self.session.get(Bankroll, int(payload["bankroll_id"]))
        stake = Decimal(str(payload["stake_amount"])).quantize(Decimal(".01"))
        if (
            bankroll is None
            or not bankroll.active
            or stake <= 0
            or bankroll.current_balance < stake
        ):
            raise ValueError("Banca, stake ou saldo inválido.")

        resolved = []
        legs_per_match: dict[int, int] = {}
        seen_selections: set[tuple[int, int, str]] = set()
        markets_per_match: dict[int, set[int]] = {}
        combined = Decimal("1")
        for item in items:
            match = self.session.get(Match, int(item["match_id"]))
            market = self.session.get(Market, int(item["market_id"]))
            if (
                match is None
                or market is None
                or not market.active
                or match.status not in {"scheduled", "not_started", "in_progress"}
            ):
                raise ValueError("Partida ou mercado indisponível.")
            selection = str(item["selection"]).strip()
            identity = (match.id, market.id, selection.casefold())
            if identity in seen_selections:
                raise ValueError(
                    "A mesma seleção não pode ser repetida no bilhete."
                )
            if market.id in markets_per_match.get(match.id, set()):
                raise ValueError(
                    "Seleções do mesmo mercado na mesma partida são incompatíveis."
                )
            legs_per_match[match.id] = legs_per_match.get(match.id, 0) + 1
            if legs_per_match[match.id] > 2:
                raise ValueError(
                    "No máximo dois mercados correlacionados por partida."
                )
            seen_selections.add(identity)
            markets_per_match.setdefault(match.id, set()).add(market.id)
            odd = self.session.scalar(
                select(Odd)
                .where(
                    Odd.match_id == match.id,
                    Odd.market_id == market.id,
                    Odd.selection == selection,
                )
                .order_by(Odd.collected_at.desc())
            )
            if odd is None:
                raise ValueError("Odd atual não encontrada.")
            prediction = self.session.scalar(
                select(Prediction)
                .where(
                    Prediction.match_id == match.id,
                    Prediction.market_id == market.id,
                    Prediction.selection == selection,
                )
                .order_by(Prediction.created_at.desc())
            )
            combined *= Decimal(str(odd.odd_value))
            resolved.append((match, market, prediction, odd, selection))

        slip = BetSlip(
            bankroll_id=bankroll.id,
            bookmaker=str(payload.get("bookmaker") or "Não informada"),
            kind="single" if len(resolved) == 1 else "multiple",
            stake_amount=stake,
            total_odds=combined,
            potential_return=(stake * combined).quantize(Decimal(".01")),
            status="pending",
        )
        self.session.add(slip)
        self.session.flush()
        for match, market, prediction, odd, selection in resolved:
            self.session.add(
                BetLeg(
                    slip_id=slip.id,
                    match_id=match.id,
                    market_id=market.id,
                    prediction_id=prediction.id if prediction else None,
                    selection=selection,
                    odd_value=odd.odd_value,
                    status="pending",
                )
            )
        before = Decimal(str(bankroll.current_balance))
        bankroll.current_balance = before - stake
        self.session.add(
            BankrollTransaction(
                bankroll_id=bankroll.id,
                slip_id=slip.id,
                transaction_type="slip_stake",
                amount=-stake,
                balance_before=before,
                balance_after=bankroll.current_balance,
                description=f"Stake do bilhete {slip.id}",
            )
        )
        self.session.commit()
        return self.get(slip.id)

    def get(self, slip_id: int) -> BetSlip:
        result = self.session.scalar(
            select(BetSlip)
            .where(BetSlip.id == slip_id)
            .options(selectinload(BetSlip.legs))
        )
        if result is None:
            raise ValueError("Bilhete não encontrado.")
        return result

    def list_all(self) -> list[BetSlip]:
        return list(
            self.session.scalars(
                select(BetSlip)
                .options(selectinload(BetSlip.legs))
                .order_by(BetSlip.placed_at.desc())
            ).all()
        )

    def settle_match(self, match: Match, statistics) -> int:
        legs = self.session.scalars(
            select(BetLeg).where(
                BetLeg.match_id == match.id, BetLeg.status == "pending"
            )
        ).all()
        affected: set[int] = set()
        now = datetime.now(timezone.utc)
        for leg in legs:
            market = self.session.get(Market, leg.market_id)
            result = evaluate_market(
                market.code,
                leg.selection,
                int(match.home_score or 0),
                int(match.away_score or 0),
                statistics.corners_home,
                statistics.corners_away,
                statistics.yellow_cards_home,
                statistics.yellow_cards_away,
                statistics.red_cards_home,
                statistics.red_cards_away,
            )
            if result == "unsupported":
                continue
            leg.result, leg.status, leg.settled_at = result, "settled", now
            affected.add(leg.slip_id)
        for slip_id in affected:
            self._finalize(self.get(slip_id), now)
        return len(affected)

    def _finalize(self, slip: BetSlip, now: datetime) -> None:
        if any(leg.status == "pending" for leg in slip.legs):
            return
        effective = Decimal("1")
        if any(leg.result == "lost" for leg in slip.legs):
            slip.status, payout = "lost", Decimal("0")
        else:
            for leg in slip.legs:
                if leg.result == "won":
                    effective *= Decimal(str(leg.odd_value))
            payout = (Decimal(str(slip.stake_amount)) * effective).quantize(
                Decimal(".01")
            )
            slip.status = "void" if effective == 1 else "won"
        slip.payout_amount, slip.settled_at = payout, now
        if payout <= 0:
            return
        bankroll = self.session.get(Bankroll, slip.bankroll_id)
        before = Decimal(str(bankroll.current_balance))
        bankroll.current_balance = before + payout
        self.session.add(
            BankrollTransaction(
                bankroll_id=bankroll.id,
                slip_id=slip.id,
                transaction_type="slip_settlement",
                amount=payout,
                balance_before=before,
                balance_after=bankroll.current_balance,
                description=f"Liquidação do bilhete {slip.id}",
            )
        )
