class CollectorError(Exception):
    """Erro genérico ocorrido durante uma coleta."""


class CollectorConnectionError(
    CollectorError
):
    """Falha de conexão com o provedor."""


class CollectorAuthenticationError(
    CollectorError
):
    """Credenciais rejeitadas pelo provedor."""


class CollectorRateLimitError(
    CollectorError
):
    """Limite de requisições atingido."""


class CollectorResponseError(
    CollectorError
):
    """Resposta inválida ou inesperada."""