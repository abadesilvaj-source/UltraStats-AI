from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.providers.base import (
    BaseProvider,
    ProviderInfo,
)
from app.providers.exceptions import (
    ProviderNotFoundError,
    ProviderRegistrationError,
)


ProviderFactory = Callable[
    ...,
    BaseProvider,
]


class ProviderRegistry:
    """
    Registro central de providers.

    Responsabilidades:

    - registrar implementações;
    - evitar nomes duplicados;
    - listar providers disponíveis;
    - criar instâncias pelo nome.
    """

    def __init__(
        self,
    ) -> None:
        self._factories: dict[
            str,
            ProviderFactory,
        ] = {}

        self._provider_info: dict[
            str,
            ProviderInfo,
        ] = {}

    @staticmethod
    def normalize_name(
        name: str,
    ) -> str:
        """
        Normaliza o nome usado para buscar
        ou registrar um provider.
        """

        normalized_name = (
            name.strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if not normalized_name:
            raise ValueError(
                "O nome do provider não pode "
                "ser vazio."
            )

        return normalized_name

    def register(
        self,
        provider_class: type[BaseProvider],
        *,
        replace: bool = False,
    ) -> type[BaseProvider]:
        """
        Registra uma classe de provider.
        """

        if not issubclass(
            provider_class,
            BaseProvider,
        ):
            raise ProviderRegistrationError(
                "A classe registrada deve herdar "
                "de BaseProvider."
            )

        provider_info = getattr(
            provider_class,
            "info",
            None,
        )

        if not isinstance(
            provider_info,
            ProviderInfo,
        ):
            raise ProviderRegistrationError(
                "O provider deve declarar o "
                "atributo de classe 'info' "
                "como ProviderInfo."
            )

        normalized_name = self.normalize_name(
            provider_info.name
        )

        if (
            normalized_name
            in self._factories
            and not replace
        ):
            raise ProviderRegistrationError(
                "Já existe um provider "
                f"registrado com o nome "
                f"'{normalized_name}'."
            )

        self._factories[
            normalized_name
        ] = provider_class

        self._provider_info[
            normalized_name
        ] = provider_info

        return provider_class

    def provider(
        self,
        provider_class: (
            type[BaseProvider] | None
        ) = None,
        *,
        replace: bool = False,
    ) -> (
        type[BaseProvider]
        | Callable[
            [type[BaseProvider]],
            type[BaseProvider],
        ]
    ):
        """
        Decorator para registrar providers.

        Uso:

        @provider_registry.provider
        class MeuProvider(BaseProvider):
            ...

        Também permite:

        @provider_registry.provider(
            replace=True
        )
        class MeuProvider(BaseProvider):
            ...
        """

        def decorator(
            target_class: type[
                BaseProvider
            ],
        ) -> type[BaseProvider]:
            return self.register(
                target_class,
                replace=replace,
            )

        if provider_class is None:
            return decorator

        return decorator(
            provider_class
        )

    def create(
        self,
        name: str,
        **kwargs: Any,
    ) -> BaseProvider:
        """
        Cria uma nova instância do provider
        registrado com o nome informado.
        """

        normalized_name = self.normalize_name(
            name
        )

        factory = self._factories.get(
            normalized_name
        )

        if factory is None:
            available_names = ", ".join(
                self.names()
            )

            available_message = (
                available_names
                if available_names
                else "nenhum"
            )

            raise ProviderNotFoundError(
                f"Provider '{normalized_name}' "
                "não encontrado. Providers "
                "disponíveis: "
                f"{available_message}."
            )

        return factory(
            **kwargs
        )

    def get_info(
        self,
        name: str,
    ) -> ProviderInfo:
        """
        Retorna as informações públicas de
        um provider registrado.
        """

        normalized_name = self.normalize_name(
            name
        )

        provider_info = (
            self._provider_info.get(
                normalized_name
            )
        )

        if provider_info is None:
            raise ProviderNotFoundError(
                f"Provider '{normalized_name}' "
                "não encontrado."
            )

        return provider_info

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Verifica se um provider está
        registrado.
        """

        normalized_name = self.normalize_name(
            name
        )

        return (
            normalized_name
            in self._factories
        )

    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Retorna os nomes registrados em
        ordem alfabética.
        """

        return tuple(
            sorted(
                self._factories
            )
        )

    def all_info(
        self,
    ) -> tuple[ProviderInfo, ...]:
        """
        Retorna as informações de todos os
        providers registrados.
        """

        return tuple(
            self._provider_info[name]
            for name in self.names()
        )


provider_registry = ProviderRegistry()