"""Monitor operacional do Motor ao Vivo."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.live import LiveStore


st.set_page_config(page_title="Motor ao Vivo", page_icon="🔴", layout="wide")
st.title("🔴 Motor ao Vivo")
st.caption("Placar, relógio, probabilidades, odds e recomendações em atualização contínua.")

with SessionLocal() as session:
    store = LiveStore(session)
    snapshots = store.recent()
    pending_push = store.pending_push()

if snapshots:
    latest_by_match = {}
    for snapshot in snapshots:
        latest_by_match.setdefault(snapshot.match_id, snapshot)
    active = list(latest_by_match.values())
    healthy = sum(item.health == "healthy" for item in active)
    degraded = sum(item.health == "degraded" for item in active)
    blocked = sum(item.health == "blocked" for item in active)
    first, second, third, fourth = st.columns(4)
    first.metric("Partidas monitoradas", len(active))
    second.metric("Saudáveis", healthy)
    third.metric("Degradadas", degraded)
    fourth.metric("Suspensas", blocked)
    st.dataframe(
        [
            {
                "partida": item.match_id,
                "tempo": item.minute,
                "placar": f"{item.home_score}–{item.away_score}",
                "fase": item.phase,
                "saúde": item.health,
                "recomendações": len(item.recommendations),
                "anomalias": len(item.anomalies),
            }
            for item in active
        ],
        use_container_width=True,
    )
else:
    st.info("Nenhuma partida ao vivo foi processada.")

st.metric("Push pendentes", len(pending_push))
st.subheader("Proteções")
st.markdown(
    """
    - ingestão idempotente e snapshots revisionados;
    - bloqueio por regressão de placar/relógio, eventos fora de ordem e saltos de odds;
    - degradação controlada para feeds atrasados;
    - suspensão automática para timeout crítico;
    - recomendações somente com fase e saúde válidas.
    """
)
