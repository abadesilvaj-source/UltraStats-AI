"""Hub unificado da experiência do UltraStats AI."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.domain.experience import (
    AlertRule,
    DataFreshness,
    ExperienceMode,
    Favorite,
    Notification,
    NotificationChannel,
    Scenario,
    SearchDocument,
    TimelineItem,
    UserExperienceProfile,
    automatic_report,
    build_timeline,
    compare_scenarios,
    natural_language_search,
)
from ultrastats_ai.infrastructure.experience import ExperienceStore


NOW = datetime.now(timezone.utc)
USER_ID = st.session_state.get("ux_user_id", "default")
DOCUMENTS = (
    SearchDocument("page", "matches", "Partidas", ("jogos", "calendário", "placar")),
    SearchDocument("page", "markets", "Mercados", ("odds", "cotações", "valor")),
    SearchDocument("page", "analysis", "Análises", ("estatísticas", "modelos", "xg")),
    SearchDocument("page", "suggestions", "Sugestões", ("recomendações", "oportunidades")),
    SearchDocument("page", "teams", "Equipes", ("clubes", "forma")),
    SearchDocument("page", "competitions", "Competições", ("ligas", "campeonatos")),
)

st.set_page_config(page_title="Experiência UltraStats", page_icon="✨", layout="wide")
st.title("✨ UltraStats AI")

mode_label = st.sidebar.radio("Modo", ("Simples", "Avançado"))
mode = ExperienceMode.SIMPLE if mode_label == "Simples" else ExperienceMode.ADVANCED
st.sidebar.caption("Atualizado agora · dados sincronizados")
freshness = DataFreshness(NOW, NOW)
st.caption(f"Modo {mode_label.lower()} · atualização: {freshness.status}")

tabs = st.tabs(
    (
        "Home",
        "Partidas",
        "Mercados",
        "Análises",
        "Sugestões",
        "Equipes",
        "Competições",
        "Favoritos",
        "Alertas",
        "Perfil",
        "Cenários",
        "Linha do tempo",
        "Busca",
        "Relatórios",
        "Notificações",
    )
)

with tabs[0]:
    st.subheader("Visão geral")
    st.write("Acesse partidas, análises, recomendações e risco em uma navegação única.")
    first, second, third = st.columns(3)
    first.metric("Modo", mode_label)
    second.metric("Dados", "Atualizados")
    third.metric("Próxima ação", "Revisar sugestões")

for tab, title, description in (
    (tabs[1], "Partidas", "Agenda, placares e contexto pré-jogo."),
    (tabs[2], "Mercados", "Odds, probabilidades e comparação de valor."),
    (tabs[3], "Análises", "Estatísticas, previsões e explicabilidade."),
    (tabs[4], "Sugestões", "Recomendações aprovadas pelos filtros de segurança."),
    (tabs[5], "Equipes", "Forma, elenco, ausências e indicadores por equipe."),
    (tabs[6], "Competições", "Ligas, temporadas, fases e desempenho agregado."),
):
    with tab:
        st.subheader(title)
        st.write(description)
        if mode is ExperienceMode.ADVANCED:
            st.info("Detalhes avançados, métricas técnicas e proveniência habilitados.")

with tabs[7]:
    st.subheader("Favoritos")
    with SessionLocal() as session:
        store = ExperienceStore(session)
        favorites = store.favorites(USER_ID)
    if favorites:
        st.dataframe(
            [
                {"tipo": item.entity_type, "id": item.entity_id, "nome": item.label}
                for item in favorites
            ],
            use_container_width=True,
        )
    else:
        st.info("Adicione equipes, competições, partidas ou mercados aos favoritos.")
    with st.form("favorite"):
        entity_type = st.selectbox("Tipo", ("team", "competition", "match", "market"))
        entity_id = st.text_input("Identificador")
        label = st.text_input("Nome")
        if st.form_submit_button("Salvar favorito"):
            with SessionLocal() as session:
                ExperienceStore(session).add_favorite(
                    Favorite(USER_ID, entity_type, entity_id, label), NOW
                )
                session.commit()
            st.success("Favorito salvo.")

with tabs[8]:
    st.subheader("Alertas")
    with st.form("alert"):
        metric = st.text_input("Métrica", value="opportunity_score")
        operator = st.selectbox("Condição", (">=", ">", "<=", "<", "=="))
        threshold = st.number_input("Limite", value=0.50)
        channel = st.selectbox("Canal", ("Dentro do aplicativo", "Push"))
        if st.form_submit_button("Criar alerta"):
            selected_channel = (
                NotificationChannel.IN_APP
                if channel == "Dentro do aplicativo"
                else NotificationChannel.PUSH
            )
            with SessionLocal() as session:
                ExperienceStore(session).save_alert(
                    AlertRule(
                        str(uuid4()),
                        USER_ID,
                        metric,
                        operator,
                        Decimal(str(threshold)),
                        selected_channel,
                    )
                )
                session.commit()
            st.success("Alerta criado.")
    st.caption("Canais externos como email, Telegram, Discord e WhatsApp não são utilizados.")

with tabs[9]:
    st.subheader("Perfil")
    reduced_motion = st.toggle("Reduzir movimento")
    high_contrast = st.toggle("Alto contraste")
    if st.button("Salvar preferências"):
        profile = UserExperienceProfile(
            USER_ID,
            mode,
            reduced_motion=reduced_motion,
            high_contrast=high_contrast,
        )
        with SessionLocal() as session:
            ExperienceStore(session).save_profile(profile, NOW)
            session.commit()
        st.success("Preferências salvas.")

with tabs[10]:
    st.subheader("Comparação de cenários")
    probability = Decimal(str(st.slider("Probabilidade", 0.01, 0.99, 0.60)))
    odds = Decimal(str(st.number_input("Odd", min_value=1.01, value=2.00)))
    stake = Decimal(str(st.number_input("Stake", min_value=0.0, value=10.0)))
    baseline = Scenario("Cenário atual", probability, odds, stake)
    conservative = Scenario("Cenário conservador", probability * Decimal(".9"), odds, stake)
    comparison = compare_scenarios((baseline, conservative))
    st.dataframe(
        [
            {"cenário": item.name, "lucro esperado": item.expected_profit}
            for item in comparison.scenarios
        ],
        use_container_width=True,
    )
    st.success(f"Melhor cenário: {comparison.best.name}")

with tabs[11]:
    st.subheader("Linha do tempo")
    items = build_timeline(
        (
            TimelineItem("sync", "dados", "Dados sincronizados", NOW),
            TimelineItem("model", "modelo", "Previsões recalculadas", NOW),
            TimelineItem("risk", "risco", "Portfólio atualizado", NOW),
        )
    )
    for item in items:
        st.write(f"**{item.title}** · {item.category} · {item.occurred_at:%H:%M}")

with tabs[12]:
    st.subheader("Busca em linguagem natural")
    query = st.text_input("O que você procura?", placeholder="análises de xG ou odds")
    results = natural_language_search(query, DOCUMENTS)
    for result in results:
        st.write(f"**{result.document.title}** · relevância {result.relevance}")
    if query and not results:
        st.info("Nenhum resultado encontrado.")

with tabs[13]:
    st.subheader("Relatórios automáticos")
    report = automatic_report(
        "Resumo UltraStats AI",
        {"modo": mode.value, "dados": freshness.status, "usuário": USER_ID},
        NOW,
    )
    st.download_button("Baixar relatório", report, "ultrastats-report.md", "text/markdown")

with tabs[14]:
    st.subheader("Notificações")
    with SessionLocal() as session:
        store = ExperienceStore(session)
        feed = store.notification_feed(USER_ID)
    if feed:
        for item in feed:
            marker = "✓" if item.read else "●"
            st.write(f"{marker} **{item.title}** — {item.body}")
    else:
        st.info("Você está em dia.")
    if st.button("Criar notificação de teste"):
        with SessionLocal() as session:
            ExperienceStore(session).notify(
                Notification(
                    str(uuid4()),
                    USER_ID,
                    "UltraStats AI",
                    "Notificações internas estão ativas.",
                    NotificationChannel.IN_APP,
                    NOW,
                )
            )
            session.commit()
        st.success("Notificação criada.")
