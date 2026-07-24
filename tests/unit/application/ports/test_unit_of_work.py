"""Testes do contrato UnitOfWork."""

import pytest

from ultrastats_ai.application.ports.unit_of_work import UnitOfWork


class RecordingUnitOfWork(UnitOfWork):
    """Implementação observável usada para validar o ciclo transacional."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def test_context_manager_returns_unit_and_closes_on_success() -> None:
    unit = RecordingUnitOfWork()

    with unit as entered:
        assert entered is unit
        entered.commit()

    assert unit.committed
    assert not unit.rolled_back
    assert unit.closed


def test_context_manager_rolls_back_and_propagates_exception() -> None:
    unit = RecordingUnitOfWork()

    with pytest.raises(RuntimeError, match="failure"):
        with unit:
            raise RuntimeError("failure")

    assert unit.rolled_back
    assert unit.closed


def test_abstract_operations_define_defensive_default_bodies() -> None:
    unit = RecordingUnitOfWork()

    with pytest.raises(NotImplementedError):
        UnitOfWork.commit(unit)

    with pytest.raises(NotImplementedError):
        UnitOfWork.rollback(unit)

    assert UnitOfWork.close(unit) is None
