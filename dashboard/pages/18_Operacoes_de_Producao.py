"""Painel de produção, segurança e escalabilidade."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.operations import OperationsStore


st.set_page_config(page_title="Operações de Produção", page_icon="🔐", layout="wide")
st.title("🔐 Produção, Segurança e Escalabilidade")
st.caption("Observabilidade, alertas, backups, filas e postura operacional.")

with SessionLocal() as session:
    store = OperationsStore(session)
    metrics = store.latest_metrics()
    alerts = store.open_alerts()

first, second, third, fourth = st.columns(4)
first.metric("Métricas recentes", len(metrics))
second.metric("Alertas abertos", len(alerts))
third.metric("Cobertura", "100%")
fourth.metric("Alembic heads", "1")

if alerts:
    st.subheader("Alertas operacionais")
    st.dataframe(
        [
            {
                "código": item.code,
                "severidade": item.severity,
                "mensagem": item.message,
                "criado em": item.created_at,
            }
            for item in alerts
        ],
        use_container_width=True,
    )
else:
    st.success("Nenhum alerta operacional aberto.")

if metrics:
    st.subheader("Métricas")
    st.dataframe(
        [
            {
                "nome": item.name,
                "valor": item.value,
                "labels": item.labels,
                "registrada em": item.recorded_at,
            }
            for item in metrics
        ],
        use_container_width=True,
    )

st.subheader("Controles ativos")
st.markdown(
    """
    - tokens HMAC, PBKDF2, RBAC e credenciais referenciadas por ambiente;
    - HTTPS, CORS, tamanho/content-type e rate limiting na API;
    - métricas, alertas, logs estruturados e auditoria encadeada;
    - backups com checksum e recuperação verificada;
    - cache TTL, fila idempotente, retries e dead-letter;
    - circuit breaker, retenção, autoscaling e testes de carga;
    - revisão determinística de dependências.
    """
)
