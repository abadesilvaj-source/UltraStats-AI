"""Contrato da unidade de trabalho da aplicação."""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class UnitOfWork(ABC):
    """Coordena uma transação de um caso de uso.

    Implementações concretas deverão ser criadas na infraestrutura.
    """

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if exception_type is not None:
            self.rollback()

        self.close()
        return False

    @abstractmethod
    def commit(self) -> None:
        """Confirma todas as alterações da transação."""

        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """Desfaz todas as alterações da transação."""

        raise NotImplementedError

    def close(self) -> None:
        """Libera os recursos utilizados pela unidade de trabalho."""