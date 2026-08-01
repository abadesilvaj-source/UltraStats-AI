import logging

from app.core.logging_config import (
    configure_logging,
)


def main() -> None:
    logger = configure_logging(
        service_name="ultrastats"
    )

    logger.debug(
        "Mensagem de depuração."
    )

    logger.info(
        "Mensagem informativa."
    )

    logger.warning(
        "Mensagem de aviso."
    )

    logger.error(
        "Mensagem de erro para teste."
    )

    try:
        result = 10 / 0
        print(result)

    except ZeroDivisionError:
        logger.exception(
            "Exceção capturada durante "
            "o teste de logging."
        )

    logging.getLogger(
        "ultrastats.teste.secundario"
    ).info(
        "Mensagem enviada por outro logger."
    )

    print(
        "\nTeste de logging concluído."
    )


if __name__ == "__main__":
    main()