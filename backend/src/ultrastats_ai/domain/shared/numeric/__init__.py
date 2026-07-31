"""Tipos numéricos compartilhados do domínio."""

from ultrastats_ai.domain.shared.numeric.age import Age
from ultrastats_ai.domain.shared.numeric.decimal_value import (
    DecimalInput,
    DecimalValue,
)
from ultrastats_ai.domain.shared.numeric.height import Height
from ultrastats_ai.domain.shared.numeric.integer_value import IntegerValue
from ultrastats_ai.domain.shared.numeric.money import Money
from ultrastats_ai.domain.shared.numeric.odds import Odds
from ultrastats_ai.domain.shared.numeric.percentage import Percentage
from ultrastats_ai.domain.shared.numeric.position import Position
from ultrastats_ai.domain.shared.numeric.probability import Probability
from ultrastats_ai.domain.shared.numeric.round_number import RoundNumber
from ultrastats_ai.domain.shared.numeric.shirt_number import ShirtNumber
from ultrastats_ai.domain.shared.numeric.weight import Weight

__all__ = [
    "Age",
    "DecimalInput",
    "DecimalValue",
    "Height",
    "IntegerValue",
    "Money",
    "Odds",
    "Percentage",
    "Position",
    "Probability",
    "RoundNumber",
    "ShirtNumber",
    "Weight",
]