"""Gestão determinística de stake, exposição, portfólio e desempenho."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Mapping


ZERO = Decimal("0")
ONE = Decimal("1")


class RiskProfileKind(StrEnum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass(frozen=True, slots=True)
class RiskProfile:
    kind: RiskProfileKind
    kelly_fraction: Decimal
    maximum_stake_fraction: Decimal
    maximum_daily_fraction: Decimal
    maximum_competition_fraction: Decimal
    maximum_market_fraction: Decimal
    maximum_correlated_positions: int = 1

    def __post_init__(self) -> None:
        fractions = (
            self.kelly_fraction,
            self.maximum_stake_fraction,
            self.maximum_daily_fraction,
            self.maximum_competition_fraction,
            self.maximum_market_fraction,
        )
        if any(value <= ZERO or value > ONE for value in fractions):
            raise ValueError("Frações do perfil devem estar no intervalo (0, 1].")
        if self.maximum_correlated_positions <= 0:
            raise ValueError("Limite de correlação deve ser positivo.")

    @classmethod
    def preset(cls, kind: RiskProfileKind) -> RiskProfile:
        presets = {
            RiskProfileKind.CONSERVATIVE: (".25", ".01", ".05", ".03", ".025", 1),
            RiskProfileKind.MODERATE: (".50", ".02", ".10", ".06", ".05", 1),
            RiskProfileKind.AGGRESSIVE: (".75", ".03", ".15", ".09", ".075", 2),
        }
        return cls(kind, *(Decimal(value) for value in presets[kind][:-1]), presets[kind][-1])


@dataclass(frozen=True, slots=True)
class BetCandidate:
    recommendation_id: str
    competition: str
    market: str
    correlation_key: str
    probability: Decimal
    odds: Decimal
    opportunity_score: Decimal

    def __post_init__(self) -> None:
        identities = (
            self.recommendation_id,
            self.competition,
            self.market,
            self.correlation_key,
        )
        if not all(value.strip() for value in identities):
            raise ValueError("Candidato exige identidades e correlação.")
        if not ZERO < self.probability <= ONE or self.odds <= ONE:
            raise ValueError("Probabilidade e odd do candidato são inválidas.")
        if self.opportunity_score < ZERO:
            raise ValueError("Opportunity Score não pode ser negativo.")


@dataclass(frozen=True, slots=True)
class PortfolioPosition:
    recommendation_id: str
    competition: str
    market: str
    correlation_key: str
    stake: Decimal
    kelly_fraction: Decimal


@dataclass(frozen=True, slots=True)
class PortfolioPlan:
    bankroll: Decimal
    positions: tuple[PortfolioPosition, ...]
    blocked: Mapping[str, tuple[str, ...]]

    @property
    def total_exposure(self) -> Decimal:
        return sum((position.stake for position in self.positions), ZERO)


@dataclass(frozen=True, slots=True)
class ExposureState:
    daily: Decimal = ZERO
    by_competition: Mapping[str, Decimal] | None = None
    by_market: Mapping[str, Decimal] | None = None
    by_correlation: Mapping[str, int] | None = None

    def __post_init__(self) -> None:
        monetary = (
            self.daily,
            *(self.by_competition or {}).values(),
            *(self.by_market or {}).values(),
        )
        if any(value < ZERO for value in monetary):
            raise ValueError("Exposições existentes não podem ser negativas.")
        if any(value < 0 for value in (self.by_correlation or {}).values()):
            raise ValueError("Contagens de correlação não podem ser negativas.")


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    total_staked: Decimal
    net_profit: Decimal
    roi: Decimal
    yield_rate: Decimal
    maximum_drawdown: Decimal


@dataclass(frozen=True, slots=True)
class SimulationResult:
    final_bankroll: Decimal
    equity_curve: tuple[Decimal, ...]
    metrics: PerformanceMetrics


def full_kelly(probability: Decimal, odds: Decimal) -> Decimal:
    if not ZERO <= probability <= ONE or odds <= ONE:
        raise ValueError("Kelly exige probabilidade válida e odd maior que um.")
    return max(ZERO, (probability * odds - ONE) / (odds - ONE))


def performance_metrics(
    initial_bankroll: Decimal,
    stakes: tuple[Decimal, ...],
    profits: tuple[Decimal, ...],
) -> PerformanceMetrics:
    if initial_bankroll <= ZERO or len(stakes) != len(profits):
        raise ValueError("Desempenho exige banca positiva e séries equivalentes.")
    if any(stake < ZERO for stake in stakes):
        raise ValueError("Stakes não podem ser negativas.")
    total_staked = sum(stakes, ZERO)
    net_profit = sum(profits, ZERO)
    equity = initial_bankroll
    peak = initial_bankroll
    maximum_drawdown = ZERO
    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        maximum_drawdown = max(maximum_drawdown, (peak - equity) / peak)
    roi = net_profit / initial_bankroll
    yield_rate = net_profit / total_staked if total_staked else ZERO
    return PerformanceMetrics(total_staked, net_profit, roi, yield_rate, maximum_drawdown)


class RiskPortfolioEngine:
    def __init__(self, profile: RiskProfile) -> None:
        self.profile = profile

    def optimize(
        self,
        bankroll: Decimal,
        candidates: tuple[BetCandidate, ...],
        exposure: ExposureState = ExposureState(),
    ) -> PortfolioPlan:
        if bankroll <= ZERO:
            raise ValueError("Banca deve ser positiva.")
        competition = dict(exposure.by_competition or {})
        market = dict(exposure.by_market or {})
        correlation = dict(exposure.by_correlation or {})
        daily = exposure.daily
        positions = []
        blocked: dict[str, tuple[str, ...]] = {}
        ordered = sorted(
            candidates,
            key=lambda item: (-item.opportunity_score, item.recommendation_id),
        )
        for candidate in ordered:
            reasons = []
            kelly = full_kelly(candidate.probability, candidate.odds)
            if kelly == ZERO:
                reasons.append("non_positive_kelly")
            if correlation.get(candidate.correlation_key, 0) >= self.profile.maximum_correlated_positions:
                reasons.append("correlation_limit")
            caps = (
                bankroll * self.profile.maximum_stake_fraction,
                bankroll * self.profile.maximum_daily_fraction - daily,
                bankroll * self.profile.maximum_competition_fraction
                - competition.get(candidate.competition, ZERO),
                bankroll * self.profile.maximum_market_fraction
                - market.get(candidate.market, ZERO),
                bankroll,
            )
            stake = min(bankroll * kelly * self.profile.kelly_fraction, *caps)
            if stake <= ZERO:
                reasons.append("exposure_limit")
            if reasons:
                blocked[candidate.recommendation_id] = tuple(reasons)
                continue
            position = PortfolioPosition(
                candidate.recommendation_id,
                candidate.competition,
                candidate.market,
                candidate.correlation_key,
                stake,
                kelly,
            )
            positions.append(position)
            daily += stake
            competition[candidate.competition] = competition.get(candidate.competition, ZERO) + stake
            market[candidate.market] = market.get(candidate.market, ZERO) + stake
            correlation[candidate.correlation_key] = correlation.get(candidate.correlation_key, 0) + 1
        return PortfolioPlan(bankroll, tuple(positions), blocked)

    def simulate(
        self,
        initial_bankroll: Decimal,
        bets: tuple[tuple[Decimal, Decimal, bool], ...],
    ) -> SimulationResult:
        if initial_bankroll <= ZERO:
            raise ValueError("Banca inicial deve ser positiva.")
        bankroll = initial_bankroll
        curve = [bankroll]
        stakes = []
        profits = []
        for probability, odds, won in bets:
            fraction = full_kelly(probability, odds) * self.profile.kelly_fraction
            stake = min(bankroll * fraction, bankroll * self.profile.maximum_stake_fraction)
            profit = stake * (odds - ONE) if won else -stake
            bankroll += profit
            stakes.append(stake)
            profits.append(profit)
            curve.append(bankroll)
        metrics = performance_metrics(initial_bankroll, tuple(stakes), tuple(profits))
        return SimulationResult(bankroll, tuple(curve), metrics)
