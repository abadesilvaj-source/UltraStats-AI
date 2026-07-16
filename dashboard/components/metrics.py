import streamlit as st


def render_home_metrics(
    performance: dict,
) -> None:
    """Exibe as métricas principais da Home."""

    column_1, column_2, column_3, column_4 = (
        st.columns(4)
    )

    column_1.metric(
        "Apostas oficiais",
        performance["total_bets"],
    )

    column_2.metric(
        "Taxa de acerto",
        f"{performance['win_rate']:.2f}%",
    )

    column_3.metric(
        "Lucro acumulado",
        f"{performance['total_profit']:.2f}u",
    )

    column_4.metric(
        "ROI",
        f"{performance['roi']:.2f}%",
    )


def render_bankroll_metrics(
    bankroll: dict,
) -> None:
    """Exibe as métricas financeiras da banca."""

    column_1, column_2, column_3, column_4 = (
        st.columns(4)
    )

    currency = bankroll["currency"]

    column_1.metric(
        "Saldo atual",
        (
            f"{currency} "
            f"{bankroll['current_balance']:.2f}"
        ),
    )

    column_2.metric(
        "Lucro líquido",
        (
            f"{currency} "
            f"{bankroll['profit']:.2f}"
        ),
        (
            f"{bankroll['profit_percentage']:.2f}%"
        ),
    )

    column_3.metric(
        "Valor de 1 unidade",
        (
            f"{currency} "
            f"{bankroll['unit_value']:.2f}"
        ),
    )

    column_4.metric(
        "Drawdown máximo",
        (
            f"{bankroll['maximum_drawdown']:.2f}%"
        ),
    )