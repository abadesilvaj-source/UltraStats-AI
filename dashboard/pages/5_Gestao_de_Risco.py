import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.database.session import SessionLocal
from dashboard.services import (
    DashboardService,
)


st.set_page_config(
    page_title="Gestão de Risco | UltraStats AI",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_bankrolls() -> list[dict]:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.get_bankrolls()

    finally:
        session.close()


@st.cache_data(ttl=30)
def load_risk_summary(
    bankroll_id: int,
) -> dict:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.get_risk_summary(
            bankroll_id
        )

    finally:
        session.close()


def simulate_stake(
    bankroll_id: int,
    probability: float,
    odd_value: float,
    profile_code: str,
) -> dict:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.simulate_stake(
            bankroll_id=bankroll_id,
            probability=probability,
            odd_value=odd_value,
            profile_code=profile_code,
        )

    finally:
        session.close()


st.title("🛡️ Gestão de Risco")

st.caption(
    "Simulação de stake, Kelly e exposição diária"
)

st.divider()


bankrolls = load_bankrolls()


if not bankrolls:
    st.warning(
        "Nenhuma banca foi cadastrada."
    )
    st.stop()


bankroll_options = {
    bankroll["name"]: bankroll["id"]
    for bankroll in bankrolls
}


selected_bankroll_name = st.selectbox(
    "Selecione a banca",
    options=list(
        bankroll_options.keys()
    ),
)


selected_bankroll_id = (
    bankroll_options[
        selected_bankroll_name
    ]
)


risk_summary = load_risk_summary(
    selected_bankroll_id
)


column_1, column_2, column_3 = (
    st.columns(3)
)


column_1.metric(
    "Saldo atual",
    f"R$ {risk_summary['balance']:.2f}",
)


column_2.metric(
    "Exposição diária",
    (
        f"R$ "
        f"{risk_summary['daily_exposure']:.2f}"
    ),
)


column_3.metric(
    "Exposição da banca",
    (
        f"{risk_summary['exposure_percentage']:.2f}%"
    ),
)


st.divider()

st.subheader("Simulador de Stake")


left_column, right_column = st.columns(2)


with left_column:
    probability_percentage = st.number_input(
        "Probabilidade estimada pelo modelo (%)",
        min_value=0.01,
        max_value=99.99,
        value=55.00,
        step=0.10,
    )

    odd_value = st.number_input(
        "Odd decimal",
        min_value=1.01,
        value=2.10,
        step=0.01,
    )


with right_column:
    profile_label = st.selectbox(
        "Perfil de risco",
        options=[
            "Conservador",
            "Moderado",
            "Agressivo",
        ],
    )

    profile_mapping = {
        "Conservador": "conservative",
        "Moderado": "moderate",
        "Agressivo": "aggressive",
    }

    profile_code = profile_mapping[
        profile_label
    ]


calculate_button = st.button(
    "Calcular stake recomendada",
    type="primary",
)


if calculate_button:
    model_probability = (
        probability_percentage / 100
    )

    try:
        recommendation = simulate_stake(
            bankroll_id=selected_bankroll_id,
            probability=model_probability,
            odd_value=odd_value,
            profile_code=profile_code,
        )

        st.divider()

        st.subheader(
            "Resultado da simulação"
        )

        if recommendation["approved"]:
            st.success(
                recommendation["reason"]
            )

            result_column_1, result_column_2, result_column_3 = (
                st.columns(3)
            )

            result_column_1.metric(
                "Stake recomendada",
                (
                    f"R$ "
                    f"{recommendation['stake_amount']:.2f}"
                ),
            )

            result_column_2.metric(
                "Stake em unidades",
                (
                    f"{recommendation['stake_units']:.2f}u"
                ),
            )

            result_column_3.metric(
                "Percentual da banca",
                (
                    f"{recommendation['stake_percentage']:.2f}%"
                ),
            )

            st.write(
                f"**Perfil:** "
                f"{recommendation['profile']}"
            )

            st.write(
                f"**EV calculado:** "
                f"{recommendation['expected_value']:.2%}"
            )

            st.write(
                f"**Kelly fracionado:** "
                f"{recommendation['fractional_kelly']:.2%}"
            )

            st.write(
                f"**Exposição atual:** "
                f"R$ "
                f"{recommendation['daily_exposure']:.2f}"
            )

            st.write(
                f"**Exposição restante permitida:** "
                f"R$ "
                f"{recommendation['remaining_daily_exposure']:.2f}"
            )

        else:
            st.error(
                recommendation["reason"]
            )

            st.write(
                f"**EV calculado:** "
                f"{recommendation['expected_value']:.2%}"
            )

    except Exception as error:
        st.error(
            f"Erro ao calcular stake: {error}"
        )


st.divider()

st.subheader("Interpretação dos perfis")


st.write(
    """
    **Conservador:** utiliza 25% do Kelly e
    limita a stake a 1% da banca.

    **Moderado:** utiliza 50% do Kelly e
    limita a stake a 2% da banca.

    **Agressivo:** utiliza 75% do Kelly e
    limita a stake a 3% da banca.
    """
)

if risk_summary["exposure_percentage"] >= 8:
    st.error(
        "Exposição crítica: evite novas apostas."
    )

elif risk_summary["exposure_percentage"] >= 5:
    st.warning(
        "Exposição elevada: analise novas entradas "
        "com cautela."
    )

elif risk_summary["exposure_percentage"] > 0:
    st.info(
        "A banca possui apostas expostas hoje."
    )

else:
    st.success(
        "Não há exposição registrada hoje."
    )