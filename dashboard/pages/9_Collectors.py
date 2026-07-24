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

@st.cache_data(ttl=10)
def load_scheduler_status() -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_scheduler_status()

    finally:
        session.close()


def execute_real_sync() -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).run_real_sync()

    finally:
        session.close()


st.title("🔄 Collectors")

st.caption(
    "Monitoramento e execução de sincronizações"
)


scheduler_status = load_scheduler_status()

persistent_status = scheduler_status[
    "persistent_status"
]


st.subheader("Status do Scheduler")


scheduler_column_1, scheduler_column_2, scheduler_column_3, scheduler_column_4 = (
    st.columns(4)
)


scheduler_column_1.metric(
    "Scheduler habilitado",
    (
        "Sim"
        if scheduler_status["enabled"]
        else "Não"
    ),
)


scheduler_column_2.metric(
    "Processo ativo",
    (
        "Sim"
        if scheduler_status["process_running"]
        else "Não"
    ),
)


scheduler_column_3.metric(
    "Job em execução",
    (
        "Sim"
        if scheduler_status["job_running"]
        else "Não"
    ),
)


scheduler_column_4.metric(
    "Intervalo",
    (
        f"{scheduler_status['interval_minutes']} min"
    ),
)

if persistent_status.get(
    "registered",
    False,
):
    st.write(
        f"**Instância:** "
        f"{persistent_status['instance_name']}"
    )

    st.write(
        f"**Host:** "
        f"{persistent_status.get('hostname') or '-'}"
    )

    st.write(
        f"**PID:** "
        f"{persistent_status.get('process_id') or '-'}"
    )

    st.write(
        f"**Último heartbeat:** "
        f"{persistent_status.get('last_heartbeat_at')}"
    )

    st.write(
        f"**Segundos desde o heartbeat:** "
        f"{persistent_status.get('seconds_since_heartbeat', 0):.1f}"
    )

    if persistent_status["online"]:
        st.success(
            "Scheduler online e enviando heartbeat."
        )

    else:
        st.error(
            "Scheduler offline ou sem heartbeat recente."
        )

    if persistent_status.get(
        "last_error"
    ):
        st.error(
            persistent_status["last_error"]
        )

else:
    st.warning(
        "Nenhuma instância do scheduler "
        "foi registrada ainda."
    )

st.write(
    f"**Provedor configurado:** "
    f"{scheduler_status['provider']}"
)


latest_database_run = (
    scheduler_status[
        "latest_database_run"
    ]
)


if latest_database_run:
    st.write(
        f"**Última execução no banco:** "
        f"ID {latest_database_run['id']} | "
        f"{latest_database_run['status']} | "
        f"{latest_database_run['triggered_by']}"
    )

    if latest_database_run[
        "error_message"
    ]:
        st.error(
            latest_database_run[
                "error_message"
            ]
        )


if not scheduler_status["process_running"]:
    st.info(
        "O Dashboard não inicia o scheduler. "
        "Execute em outro terminal: "
        "`python -m scripts.run_scheduler`"
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
    "Executa o pipeline real multi-provider, incluindo partidas, odds e "
    "previsões. A operação consome a cota das APIs configuradas."
)


confirmation = st.checkbox(
    "Confirmo que desejo executar "
    "uma sincronização real agora."
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
            execution = execute_real_sync()

        load_sync_history.clear()
        load_scheduler_status.clear()
        st.cache_data.clear()

        st.success(
            "Sincronização concluída com sucesso."
        )

        result = execution["operational"]

        summary_1, summary_2, summary_3 = (
            st.columns(3)
        )

        summary_1.metric(
            "Competições",
            result["competitions"],
        )

        summary_2.metric(
            "Equipes",
            result["teams"],
        )

        summary_3.metric(
            "Partidas",
            result["matches"],
        )

        st.write(
            f"**Execução ID:** "
            f"{execution['sync_run_id']}"
        )

        st.write(
            f"**Duração:** "
            f"{execution['duration_seconds']:.4f}s"
        )
        st.write(
            f"**Previsões atualizadas:** "
            f"{result['predictions']}"
        )
        if execution["degraded"]:
            st.warning(
                "A sincronização terminou em modo degradado: uma ou mais "
                "fontes falharam, mas os dados disponíveis foram processados."
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

    display_history = history_df[
        [
            "id",
            "source",
            "status",
            "started_at",
            "duration_seconds",
            "matches_created",
            "matches_updated",
            "triggered_by",
            "error_message",
        ]
    ].rename(
        columns={
            "id": "Execução",
            "source": "Fonte",
            "status": "Status",
            "started_at": "Início",
            "duration_seconds": "Duração (s)",
            "matches_created": "Itens novos",
            "matches_updated": "Itens atualizados",
            "triggered_by": "Acionamento",
            "error_message": "Erro",
        }
    )

    st.dataframe(
        display_history,
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
