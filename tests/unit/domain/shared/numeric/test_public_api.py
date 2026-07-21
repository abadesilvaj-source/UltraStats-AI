"""Testes da API pública dos tipos numéricos."""

from ultrastats_ai.domain.shared import (
    Age,
    DecimalValue,
    Height,
    IntegerValue,
    Money,
    Odds,
    Percentage,
    Position,
    Probability,
    RoundNumber,
    ShirtNumber,
    Weight,
)
from ultrastats_ai.domain.shared.numeric import (
    Age as NumericAge,
    DecimalValue as NumericDecimalValue,
    Height as NumericHeight,
    IntegerValue as NumericIntegerValue,
    Money as NumericMoney,
    Odds as NumericOdds,
    Percentage as NumericPercentage,
    Position as NumericPosition,
    Probability as NumericProbability,
    RoundNumber as NumericRoundNumber,
    ShirtNumber as NumericShirtNumber,
    Weight as NumericWeight,
)


def test_numeric_types_are_exported_by_public_apis() -> None:
    assert Age is NumericAge
    assert DecimalValue is NumericDecimalValue
    assert Height is NumericHeight
    assert IntegerValue is NumericIntegerValue
    assert Money is NumericMoney
    assert Odds is NumericOdds
    assert Percentage is NumericPercentage
    assert Position is NumericPosition
    assert Probability is NumericProbability
    assert RoundNumber is NumericRoundNumber
    assert ShirtNumber is NumericShirtNumber
    assert Weight is NumericWeight