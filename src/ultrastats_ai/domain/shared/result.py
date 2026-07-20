"""Tipo explícito para resultados de operações."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, cast

from ultrastats_ai.domain.shared.errors import ResultAccessError

ValueType = TypeVar("ValueType")
ErrorType = TypeVar("ErrorType")


@dataclass(frozen=True, slots=True)
class Result(Generic[ValueType, ErrorType]):
    """Representa o sucesso ou a falha de uma operação.

    Um Result nunca deve possuir valor e erro simultaneamente.
    """

    _value: ValueType | None = None
    _error: ErrorType | None = None
    _is_success: bool = False

    def __post_init__(self) -> None:
        if self._is_success and self._error is not None:
            raise ValueError("Um resultado de sucesso não pode possuir erro.")

        if not self._is_success and self._error is None:
            raise ValueError("Um resultado de falha deve possuir um erro.")

    @classmethod
    def success(
        cls,
        value: ValueType,
    ) -> Result[ValueType, ErrorType]:
        """Cria um resultado de sucesso."""

        return cls(
            _value=value,
            _error=None,
            _is_success=True,
        )

    @classmethod
    def failure(
        cls,
        error: ErrorType,
    ) -> Result[ValueType, ErrorType]:
        """Cria um resultado de falha."""

        if error is None:
            raise ValueError("O erro do resultado não pode ser None.")

        return cls(
            _value=None,
            _error=error,
            _is_success=False,
        )

    @property
    def is_success(self) -> bool:
        """Indica se a operação foi concluída com sucesso."""

        return self._is_success

    @property
    def is_failure(self) -> bool:
        """Indica se a operação terminou em falha."""

        return not self._is_success

    @property
    def value(self) -> ValueType:
        """Retorna o valor de sucesso.

        Raises:
            ResultAccessError: quando chamado em um resultado de falha.
        """

        if self.is_failure:
            raise ResultAccessError(
                "Não é possível acessar o valor de um resultado de falha."
            )

        return cast(ValueType, self._value)

    @property
    def error(self) -> ErrorType:
        """Retorna o erro da operação.

        Raises:
            ResultAccessError: quando chamado em um resultado de sucesso.
        """

        if self.is_success:
            raise ResultAccessError(
                "Não é possível acessar o erro de um resultado de sucesso."
            )

        return cast(ErrorType, self._error)

    def value_or(self, default: ValueType) -> ValueType:
        """Retorna o valor ou um valor padrão em caso de falha."""

        if self.is_success:
            return cast(ValueType, self._value)

        return default