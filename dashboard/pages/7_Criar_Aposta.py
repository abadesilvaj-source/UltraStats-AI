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
    page_title=(
        "Criar Aposta | UltraStats AI"
    ),
    page_icon="📝",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_form_data() -> dict:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.get_betting_form_data()

    finally:
        session.close()


def simulate_bet(
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


def create_bet(
    **bet_data,
) -> dict:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.create_managed_bet(
            **bet_data
        )

    finally:
        session.close()


st.title("📝 Criar Aposta Oficial")

st.caption(
    "Registro manual de análise, risco e aposta"
)

st.divider()


form_data = load_form_data()

matches = form_data["matches"]
markets = form_data["markets"]
bankrolls = form_data["bankrolls"]


if not matches:
    st.warning(
        "Não existem partidas abertas "
        "para receber apostas."
    )
    st.stop()


if not markets:
    st.warning(
        "Não existem mercados ativos."
    )
    st.stop()


if not bankrolls:
    st.warning(
        "Não existe banca ativa."
    )
    st.stop()


match_options = {
    match["label"]: match
    for match in matches
}


market_options = {
    market["label"]: market
    for market in markets
}


bankroll_options = {
    bankroll["label"]: bankroll
    for bankroll in bankrolls
}


st.subheader("1. Contexto da aposta")


column_1, column_2 = st.columns(2)


with column_1:
    selected_match_label = st.selectbox(
        "Partida",
        options=list(
            match_options.keys()
        ),
    )

    selected_market_label = st.selectbox(
        "Mercado",
        options=list(
            market_options.keys()
        ),
    )

    selection = st.text_input(
        "Seleção",
        value="Mais de 2.5 gols",
        help=(
            "Exemplo: Mandante, Empate, "
            "Mais de 2.5 gols ou Sim."
        ),
    )


with column_2:
    selected_bankroll_label = (
        st.selectbox(
            "Banca",
            options=list(
                bankroll_options.keys()
            ),
        )
    )

    bookmaker = st.text_input(
        "Casa de apostas",
        value="Casa de Teste",
    )

    model_version = st.text_input(
        "Versão do modelo",
        value="0.3.0",
    )


st.divider()

st.subheader("2. Probabilidade e odd")


column_3, column_4 = st.columns(2)


with column_3:
    probability_percentage = (
        st.number_input(
            "Probabilidade do modelo (%)",
            min_value=0.01,
            max_value=99.99,
            value=55.00,
            step=0.10,
        )
    )

    odd_value = st.number_input(
        "Odd decimal",
        min_value=1.01,
        value=2.10,
        step=0.01,
    )


with column_4:
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

    evidence_level = st.selectbox(
        "Nível de evidência",
        options=[
            "A",
            "B",
            "C",
            "D",
        ],
        index=1,
    )

    risk_level = st.selectbox(
        "Classificação qualitativa do risco",
        options=[
            "Baixo",
            "Médio",
            "Alto",
        ],
        index=1,
    )


st.divider()

st.subheader("3. Scores do modelo")


score_column_1, score_column_2 = (
    st.columns(2)
)


with score_column_1:
    confidence = st.slider(
        "Confiança",
        min_value=0.0,
        max_value=100.0,
        value=78.0,
        step=1.0,
    )

    uqs = st.slider(
        "UQS",
        min_value=0.0,
        max_value=100.0,
        value=82.0,
        step=1.0,
    )


with score_column_2:
    use_score = st.slider(
        "USE Score",
        min_value=0.0,
        max_value=100.0,
        value=80.0,
        step=1.0,
    )

    confluence = st.slider(
        "Confluência",
        min_value=0.0,
        max_value=100.0,
        value=75.0,
        step=1.0,
    )


selected_match = match_options[
    selected_match_label
]

selected_market = market_options[
    selected_market_label
]

selected_bankroll = bankroll_options[
    selected_bankroll_label
]

profile_code = profile_mapping[
    profile_label
]

model_probability = (
    probability_percentage / 100
)


st.divider()

simulation_column, registration_column = (
    st.columns(2)
)


with simulation_column:
    simulate_button = st.button(
        "Simular aposta",
        use_container_width=True,
    )


with registration_column:
    register_button = st.button(
        "Registrar aposta oficial",
        type="primary",
        use_container_width=True,
    )


if simulate_button:
    try:
        recommendation = simulate_bet(
            bankroll_id=(
                selected_bankroll["id"]
            ),
            probability=model_probability,
            odd_value=odd_value,
            profile_code=profile_code,
        )

        st.subheader(
            "Resultado da simulação"
        )

        if recommendation["approved"]:
            st.success(
                recommendation["reason"]
            )

            metric_1, metric_2, metric_3, metric_4 = (
                st.columns(4)
            )

            metric_1.metric(
                "EV",
                (
                    f"{recommendation['expected_value']:.2%}"
                ),
            )

            metric_2.metric(
                "Stake",
                (
                    f"{selected_bankroll['currency']} "
                    f"{recommendation['stake_amount']:.2f}"
                ),
            )

            metric_3.metric(
                "Unidades",
                (
                    f"{recommendation['stake_units']:.2f}u"
                ),
            )

            metric_4.metric(
                "% da banca",
                (
                    f"{recommendation['stake_percentage']:.2f}%"
                ),
            )

            st.write(
                f"**Perfil:** "
                f"{recommendation['profile']}"
            )

            st.write(
                f"**Kelly fracionado:** "
                f"{recommendation['fractional_kelly']:.2%}"
            )

        else:
            st.error(
                recommendation["reason"]
            )

    except Exception as error:
        st.error(
            f"Erro na simulação: {error}"
        )


if register_button:
    try:
        if not selection.strip():
            raise ValueError(
                "A seleção é obrigatória."
            )

        if not bookmaker.strip():
            raise ValueError(
                "A casa de apostas é obrigatória."
            )

        confirmation = create_bet(
            bankroll_id=(
                selected_bankroll["id"]
            ),
            match_external_id=(
                selected_match["external_id"]
            ),
            market_code=(
                selected_market["code"]
            ),
            bookmaker=bookmaker.strip(),
            selection=selection.strip(),
            odd_value=odd_value,
            model_probability=(
                model_probability
            ),
            profile_code=profile_code,
            model_version=(
                model_version.strip()
            ),
            confidence=confidence,
            uqs=uqs,
            use_score=use_score,
            confluence=confluence,
            evidence_level=(
                evidence_level
            ),
            risk_level=risk_level,
        )

        load_form_data.clear()

        st.success(
            "Aposta oficial registrada com sucesso!"
        )

        st.write(
            f"**Aposta ID:** "
            f"{confirmation['bet_id']}"
        )

        st.write(
            f"**Seleção:** "
            f"{confirmation['selection']}"
        )

        st.write(
            f"**Odd:** "
            f"{confirmation['odd']:.2f}"
        )

        st.write(
            f"**Stake:** "
            f"{selected_bankroll['currency']} "
            f"{confirmation['stake_amount']:.2f}"
        )

        st.write(
            f"**Unidades:** "
            f"{confirmation['stake_units']:.2f}u"
        )

        st.write(
            f"**EV:** "
            f"{confirmation['expected_value']:.2%}"
        )

        st.info(
            "A stake foi debitada automaticamente "
            "da banca selecionada."
        )

    except Exception as error:
        st.error(
            f"Erro ao registrar aposta: {error}"
        )