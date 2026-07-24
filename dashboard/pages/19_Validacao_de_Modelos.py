"""Painel explicativo do gate de modelos."""

import streamlit as st


st.set_page_config(page_title="Validação de Modelos", page_icon="🧪", layout="wide")
st.title("🧪 Validação de Modelos")
st.caption("Backtesting temporal, calibração e critérios para promoção.")

st.subheader("Fluxo obrigatório")
st.code(
    "dataset versionado → split temporal → backtest rolling → calibração "
    "→ gate de métricas → aprovação"
)

st.subheader("Métricas")
st.dataframe(
    [
        {"Métrica": "Brier score", "Interpretação": "Erro quadrático das probabilidades", "Melhor": "Menor"},
        {"Métrica": "Log loss", "Interpretação": "Penaliza previsões erradas e confiantes", "Melhor": "Menor"},
        {"Métrica": "Calibration error", "Interpretação": "Distância entre confiança e frequência", "Melhor": "Menor"},
        {"Métrica": "Acurácia", "Interpretação": "Classe mais provável correta", "Melhor": "Maior"},
        {"Métrica": "ROI simulado", "Interpretação": "Retorno histórico com odds disponíveis", "Melhor": "Contextual"},
    ],
    use_container_width=True,
)

st.warning(
    "ROI isolado não aprova um modelo. A promoção depende de amostra mínima, "
    "qualidade probabilística, calibração e ausência de vazamento temporal."
)
