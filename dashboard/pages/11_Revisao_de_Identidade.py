"""Fila operacional de revisão de identidades e quarentena."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.identity import IdentityFusionStore


st.set_page_config(page_title="Revisão de Identidade", page_icon="🔎", layout="wide")
st.title("🔎 Revisão de Identidade")
st.caption("Decisões pendentes, evidências e payloads em quarentena.")

with SessionLocal() as session:
    store = IdentityFusionStore(session)
    reviews = store.review_queue()
    quarantined = store.pending_quarantine()

st.subheader("Revisão manual")
if reviews:
    st.dataframe(
        [
            {
                "Provider": item.provider,
                "ID externo": item.external_id,
                "Candidato": item.candidate.canonical_id if item.candidate else None,
                "Confiança": float(item.candidate.score) if item.candidate else None,
                "Motivo": item.reason,
            }
            for item in reviews
        ],
        use_container_width=True,
    )
else:
    st.success("Nenhuma decisão aguardando revisão.")

st.subheader("Quarentena")
if quarantined:
    st.dataframe(
        [
            {
                "Provider": item.provider,
                "Recurso": item.resource,
                "Fingerprint": item.payload_fingerprint,
                "Motivo": item.reason,
                "Tentativas": item.attempts,
            }
            for item in quarantined
        ],
        use_container_width=True,
    )
else:
    st.success("Nenhum payload em quarentena.")
