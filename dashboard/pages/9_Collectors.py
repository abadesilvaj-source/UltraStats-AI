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
    page_title="Collectors | UltraStats AI",
    page_icon="🔄",
    layout="wide",
)


@st.cache_data(ttl=15)
def load_sync_history() -> list[dict]:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_sync_history(
            limit=100
        )

    finally:
        session.close()


def execute_mock_sync() -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).run_mock_sync()

    finally:
        session.close()


st.title("🔄 Collectors")

st.caption(
    "Monitoramento e execução de sincronizações"
)

st.divider()


history = load_sync_history()


latest_run = (
    history[0]
    if history
    else None
)


metric_1, metric_2, metric_3, metric_4 = (
    st.columns(4)
)


if latest_run:
    metric_1.metric(
        "Última execução",
        latest_run["source"],
    )

    metric_2.metric(
        "Status",
        latest_run["status"],
    )

    metric_3.metric(
        "Duração",
        (
            f"{latest_run['duration_seconds']:.2f}s"
            if latest_run[
                "duration_seconds"
            ] is not None
            else "-"
        ),
    )

    metric_4.metric(
        "Acionamento",
        latest_run["triggered_by"],
    )

else:
    metric_1.metric(
        "Última execução",
        "Nenhuma",
    )

    metric_2.metric(
        "Status",
        "-",
    )

    metric_3.metric(
        "Duração",
        "-",
    )

    metric_4.metric(
        "Acionamento",
        "-",
    )


st.divider()

st.subheader("Execução manual")


st.info(
    "O provedor mock lê o arquivo local "
    "`data/providers/mock_sports_data.json`."
)


confirmation = st.checkbox(
    "Confirmo que desejo executar "
    "a sincronização do provedor mock."
)


run_button = st.button(
    "Executar sincronização",
    type="primary",
)


if run_button:
    try:
        if not confirmation:
            raise ValueError(
                "Confirme a execução antes de continuar."
            )

        with st.spinner(
            "Executando sincronização..."
        ):
            execution = execute_mock_sync()

        load_sync_history.clear()

        st.success(
            "Sincronização concluída com sucesso."
        )

        result = execution["result"]

        summary_1, summary_2, summary_3 = (
            st.columns(3)
        )

        summary_1.metric(
            "Competições",
            result["competitions"]["total"],
        )

        summary_2.metric(
            "Equipes",
            result["teams"]["total"],
        )

        summary_3.metric(
            "Partidas",
            result["matches"]["total"],
        )

        st.write(
            f"**Execução ID:** "
            f"{execution['sync_run_id']}"
        )

        st.write(
            f"**Duração:** "
            f"{execution['duration_seconds']:.4f}s"
        )

    except Exception as error:
        load_sync_history.clear()

        st.error(
            f"Erro na sincronização: {error}"
        )


st.divider()

st.subheader("Histórico de sincronizações")


history = load_sync_history()


if not history:
    st.info(
        "Nenhuma sincronização foi registrada."
    )

else:
    history_df = pd.DataFrame(
        history
    )

    status_filter = st.selectbox(
        "Filtrar por status",
        options=[
            "Todos",
            "started",
            "success",
            "failed",
        ],
    )

    if status_filter != "Todos":
        history_df = history_df[
            history_df["status"]
            == status_filter
        ]

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
    )


    failed_runs = history_df[
        history_df["status"]
        == "failed"
    ]

    if not failed_runs.empty:
        st.subheader(
            "Falhas recentes"
        )

        for _, row in failed_runs.iterrows():
            st.error(
                (
                    f"Execução {row['id']} | "
                    f"{row['source']} | "
                    f"{row['error_message']}"
                )
            )