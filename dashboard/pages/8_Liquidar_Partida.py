import sys
from pathlib import Path

import pandas as pd
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
        "Liquidar Partida | UltraStats AI"
    ),
    page_icon="✅",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_settlement_data() -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_settlement_form_data()

    finally:
        session.close()


def execute_settlement(
    **settlement_data,
) -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).settle_match_administratively(
            **settlement_data
        )

    finally:
        session.close()


st.title("✅ Liquidação Administrativa")

st.caption(
    "Registro do resultado oficial e "
    "liquidação automática das apostas"
)

st.divider()


form_data = load_settlement_data()

matches = form_data["matches"]


if not matches:
    st.info(
        "Não existem partidas abertas "
        "para liquidação."
    )
    st.stop()


match_options = {
    match["label"]: match
    for match in matches
}


selected_match_label = st.selectbox(
    "Selecione a partida",
    options=list(
        match_options.keys()
    ),
)


selected_match = match_options[
    selected_match_label
]


information_column_1, information_column_2 = (
    st.columns(2)
)


with information_column_1:
    st.write(
        f"**Mandante:** "
        f"{selected_match['home_team']}"
    )

    st.write(
        f"**Visitante:** "
        f"{selected_match['away_team']}"
    )

    st.write(
        f"**Competição:** "
        f"{selected_match['competition']}"
    )


with information_column_2:
    st.write(
        f"**Data:** "
        f"{selected_match['kickoff_at']:%d/%m/%Y %H:%M}"
    )

    st.write(
        f"**Status:** "
        f"{selected_match['status']}"
    )

    st.write(
        f"**Apostas pendentes:** "
        f"{selected_match['pending_bets']}"
    )


if selected_match["pending_bets"] == 0:
    st.warning(
        "Essa partida não possui apostas pendentes. "
        "O resultado e as estatísticas ainda poderão "
        "ser registrados."
    )


st.divider()

st.subheader("1. Placar oficial")


score_column_1, score_column_2 = (
    st.columns(2)
)


with score_column_1:
    home_score = st.number_input(
        (
            f"Gols — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )


with score_column_2:
    away_score = st.number_input(
        (
            f"Gols — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )


source = st.text_input(
    "Fonte oficial",
    value="",
    help=(
        "Exemplo: site oficial da competição, "
        "FIFA, federação ou provedor licenciado."
    ),
)


st.divider()

st.subheader("2. Escanteios e cartões")


stat_column_1, stat_column_2 = (
    st.columns(2)
)


with stat_column_1:
    corners_home = st.number_input(
        (
            f"Escanteios — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    yellow_cards_home = st.number_input(
        (
            f"Cartões amarelos — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    red_cards_home = st.number_input(
        (
            f"Cartões vermelhos — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )


with stat_column_2:
    corners_away = st.number_input(
        (
            f"Escanteios — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    yellow_cards_away = st.number_input(
        (
            f"Cartões amarelos — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    red_cards_away = st.number_input(
        (
            f"Cartões vermelhos — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )


st.divider()

st.subheader("3. Finalizações e impedimentos")


attack_column_1, attack_column_2 = (
    st.columns(2)
)


with attack_column_1:
    shots_home = st.number_input(
        (
            f"Finalizações — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    shots_on_target_home = st.number_input(
        (
            f"Finalizações no gol — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    offsides_home = st.number_input(
        (
            f"Impedimentos — "
            f"{selected_match['home_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )


with attack_column_2:
    shots_away = st.number_input(
        (
            f"Finalizações — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    shots_on_target_away = st.number_input(
        (
            f"Finalizações no gol — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )

    offsides_away = st.number_input(
        (
            f"Impedimentos — "
            f"{selected_match['away_team']}"
        ),
        min_value=0,
        value=0,
        step=1,
    )


st.divider()

st.subheader("4. Posse de bola e xG")


advanced_column_1, advanced_column_2 = (
    st.columns(2)
)


with advanced_column_1:
    possession_home = st.number_input(
        (
            f"Posse de bola (%) — "
            f"{selected_match['home_team']}"
        ),
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=0.1,
    )

    xg_home = st.number_input(
        (
            f"xG — "
            f"{selected_match['home_team']}"
        ),
        min_value=0.0,
        value=0.0,
        step=0.01,
    )


with advanced_column_2:
    possession_away = st.number_input(
        (
            f"Posse de bola (%) — "
            f"{selected_match['away_team']}"
        ),
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=0.1,
    )

    xg_away = st.number_input(
        (
            f"xG — "
            f"{selected_match['away_team']}"
        ),
        min_value=0.0,
        value=0.0,
        step=0.01,
    )


st.divider()

st.warning(
    "A liquidação altera a partida, as apostas, "
    "a banca e as auditorias. Confira todos os "
    "dados antes de confirmar."
)


confirmation = st.checkbox(
    "Confirmo que os dados informados são oficiais "
    "e desejo encerrar a partida."
)


settle_button = st.button(
    "Liquidar partida",
    type="primary",
    use_container_width=True,
)


if settle_button:
    try:
        if not confirmation:
            raise ValueError(
                "Confirme a liquidação antes de continuar."
            )

        if not source.strip():
            raise ValueError(
                "Informe a fonte oficial."
            )

        if shots_on_target_home > shots_home:
            raise ValueError(
                "As finalizações no gol do mandante "
                "não podem superar o total de finalizações."
            )

        if shots_on_target_away > shots_away:
            raise ValueError(
                "As finalizações no gol do visitante "
                "não podem superar o total de finalizações."
            )

        result = execute_settlement(
            match_external_id=(
                selected_match["external_id"]
            ),
            home_score=int(home_score),
            away_score=int(away_score),
            source=source.strip(),
            corners_home=int(corners_home),
            corners_away=int(corners_away),
            yellow_cards_home=int(
                yellow_cards_home
            ),
            yellow_cards_away=int(
                yellow_cards_away
            ),
            red_cards_home=int(
                red_cards_home
            ),
            red_cards_away=int(
                red_cards_away
            ),
            shots_home=int(shots_home),
            shots_away=int(shots_away),
            shots_on_target_home=int(
                shots_on_target_home
            ),
            shots_on_target_away=int(
                shots_on_target_away
            ),
            offsides_home=int(
                offsides_home
            ),
            offsides_away=int(
                offsides_away
            ),
            possession_home=float(
                possession_home
            ),
            possession_away=float(
                possession_away
            ),
            xg_home=float(xg_home),
            xg_away=float(xg_away),
        )

        load_settlement_data.clear()

        st.success(
            "Partida liquidada com sucesso!"
        )

        summary_column_1, summary_column_2, summary_column_3 = (
            st.columns(3)
        )

        summary_column_1.metric(
            "Placar",
            (
                f"{result['home_score']} x "
                f"{result['away_score']}"
            ),
        )

        summary_column_2.metric(
            "Apostas liquidadas",
            result["settled_bets_count"],
        )

        summary_column_3.metric(
            "Lucro total",
            (
                f"{result['total_profit_units']:.2f}u"
            ),
        )

        settled_bets = result[
            "settled_bets"
        ]

        if settled_bets:
            st.subheader(
                "Resultado das apostas"
            )

            bets_df = pd.DataFrame(
                settled_bets
            )

            st.dataframe(
                bets_df,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info(
                "Nenhuma aposta pendente estava "
                "vinculada a esta partida."
            )

        st.info(
            "Os painéis de Banca, Apostas, "
            "Performance e Análises foram atualizados."
        )

    except Exception as error:
        st.error(
            f"Erro ao liquidar partida: {error}"
        )