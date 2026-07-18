from __future__ import annotations


class ProviderError(Exception):
    """
    Exceção base para erros relacionados
    aos provedores externos.
    """


class ProviderConfigurationError(
    ProviderError
):
    """
    Indica erro de configuração, como
    URL ou chave de API ausente.
    """


class ProviderNetworkError(
    ProviderError
):
    """
    Indica falha de rede, timeout ou
    impossibilidade de acessar a API.
    """


class ProviderResponseError(
    ProviderError
):
    """
    Indica que o provedor respondeu com
    um status HTTP de erro.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        url: str | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(
            message
        )

        self.status_code = status_code
        self.url = url
        self.response_text = response_text


class ProviderRateLimitError(
    ProviderResponseError
):
    """
    Indica que o limite de requisições
    do provedor foi atingido.
    """


class ProviderDataError(
    ProviderError
):
    """
    Indica que a resposta recebida não
    possui o formato esperado.
    """