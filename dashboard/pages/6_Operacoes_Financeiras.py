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
        "Operações Financeiras | UltraStats AI"
    ),
    page_icon="🏦",
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


def execute_create_bankroll(
    name: str,
    initial_balance: float,
    currency: str,
    unit_percentage: float,
) -> dict:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.create_bankroll(
            name=name,
            initial_balance=initial_balance,
            currency=currency,
            unit_percentage=unit_percentage,
        )

    finally:
        session.close()


def execute_deposit(
    bankroll_id: int,
    amount: float,
    description: str | None,
) -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).deposit_to_bankroll(
            bankroll_id=bankroll_id,
            amount=amount,
            description=description,
        )

    finally:
        session.close()


def execute_withdrawal(
    bankroll_id: int,
    amount: float,
    description: str | None,
) -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).withdraw_from_bankroll(
            bankroll_id=bankroll_id,
            amount=amount,
            description=description,
        )

    finally:
        session.close()


def execute_adjustment(
    bankroll_id: int,
    amount: float,
    description: str,
) -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).adjust_bankroll(
            bankroll_id=bankroll_id,
            amount=amount,
            description=description,
        )

    finally:
        session.close()


def execute_status_change(
    bankroll_id: int,
    active: bool,
) -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).set_bankroll_status(
            bankroll_id=bankroll_id,
            active=active,
        )

    finally:
        session.close()


st.title("🏦 Operações Financeiras")

st.caption(
    "Criação, depósitos, retiradas e ajustes de banca"
)

st.divider()


tab_create, tab_deposit, tab_withdraw, tab_adjust, tab_status = (
    st.tabs(
        [
            "Criar banca",
            "Depósito",
            "Retirada",
            "Ajuste manual",
            "Status",
        ]
    )
)


with tab_create:
    st.subheader("Criar uma nova banca")

    with st.form(
        "create_bankroll_form"
    ):
        name = st.text_input(
            "Nome da banca",
            value="",
        )

        initial_balance = st.number_input(
            "Saldo inicial",
            min_value=0.01,
            value=1000.00,
            step=10.00,
        )

        currency = st.selectbox(
            "Moeda",
            [
                "BRL",
                "USD",
                "EUR",
            ],
        )

        unit_percentage = st.number_input(
            "Percentual de 1 unidade",
            min_value=0.01,
            max_value=100.00,
            value=1.00,
            step=0.10,
        )

        create_button = st.form_submit_button(
            "Criar banca",
            type="primary",
        )

    if create_button:
        try:
            if not name.strip():
                raise ValueError(
                    "Informe o nome da banca."
                )

            result = execute_create_bankroll(
                name=name.strip(),
                initial_balance=initial_balance,
                currency=currency,
                unit_percentage=unit_percentage,
            )

            load_bankrolls.clear()

            st.success(
                f"Banca '{result['name']}' "
                "criada com sucesso."
            )

            st.write(
                f"Saldo atual: "
                f"{result['currency']} "
                f"{result['current_balance']:.2f}"
            )

        except Exception as error:
            st.error(
                f"Erro ao criar banca: {error}"
            )


bankrolls = load_bankrolls()


if bankrolls:
    bankroll_options = {
        (
            f"{bankroll['name']} "
            f"({'Ativa' if bankroll['active'] else 'Inativa'})"
        ): bankroll["id"]
        for bankroll in bankrolls
    }

else:
    bankroll_options = {}


with tab_deposit:
    st.subheader("Realizar depósito")

    if not bankroll_options:
        st.warning(
            "Nenhuma banca cadastrada."
        )

    else:
        selected_deposit_bankroll = (
            st.selectbox(
                "Banca",
                options=list(
                    bankroll_options.keys()
                ),
                key="deposit_bankroll",
            )
        )

        deposit_amount = st.number_input(
            "Valor do depósito",
            min_value=0.01,
            value=100.00,
            step=10.00,
        )

        deposit_description = st.text_input(
            "Descrição",
            value="Depósito manual",
            key="deposit_description",
        )

        if st.button(
            "Confirmar depósito",
            type="primary",
        ):
            try:
                bankroll_id = bankroll_options[
                    selected_deposit_bankroll
                ]

                result = execute_deposit(
                    bankroll_id=bankroll_id,
                    amount=deposit_amount,
                    description=deposit_description,
                )

                load_bankrolls.clear()

                st.success(
                    "Depósito realizado com sucesso."
                )

                st.write(
                    f"Novo saldo: "
                    f"R$ "
                    f"{result['balance_after']:.2f}"
                )

            except Exception as error:
                st.error(
                    f"Erro ao depositar: {error}"
                )


with tab_withdraw:
    st.subheader("Realizar retirada")

    if not bankroll_options:
        st.warning(
            "Nenhuma banca cadastrada."
        )

    else:
        selected_withdraw_bankroll = (
            st.selectbox(
                "Banca",
                options=list(
                    bankroll_options.keys()
                ),
                key="withdraw_bankroll",
            )
        )

        withdrawal_amount = st.number_input(
            "Valor da retirada",
            min_value=0.01,
            value=100.00,
            step=10.00,
            key="withdraw_amount",
        )

        withdrawal_description = st.text_input(
            "Descrição",
            value="Retirada manual",
            key="withdraw_description",
        )

        confirm_withdrawal = st.checkbox(
            "Confirmo que desejo realizar a retirada",
        )

        if st.button(
            "Confirmar retirada",
            type="primary",
        ):
            try:
                if not confirm_withdrawal:
                    raise ValueError(
                        "Confirme a retirada antes de continuar."
                    )

                bankroll_id = bankroll_options[
                    selected_withdraw_bankroll
                ]

                result = execute_withdrawal(
                    bankroll_id=bankroll_id,
                    amount=withdrawal_amount,
                    description=(
                        withdrawal_description
                    ),
                )

                load_bankrolls.clear()

                st.success(
                    "Retirada realizada com sucesso."
                )

                st.write(
                    f"Novo saldo: "
                    f"R$ "
                    f"{result['balance_after']:.2f}"
                )

            except Exception as error:
                st.error(
                    f"Erro ao retirar: {error}"
                )


with tab_adjust:
    st.subheader("Ajuste administrativo")

    st.warning(
        "Use ajustes manuais apenas para corrigir "
        "diferenças comprovadas."
    )

    if not bankroll_options:
        st.warning(
            "Nenhuma banca cadastrada."
        )

    else:
        selected_adjust_bankroll = (
            st.selectbox(
                "Banca",
                options=list(
                    bankroll_options.keys()
                ),
                key="adjust_bankroll",
            )
        )

        adjustment_amount = st.number_input(
            "Valor do ajuste",
            value=0.00,
            step=1.00,
            help=(
                "Use valor positivo para aumentar "
                "e negativo para reduzir o saldo."
            ),
        )

        adjustment_description = st.text_area(
            "Motivo obrigatório",
            value="",
        )

        if st.button(
            "Aplicar ajuste",
            type="primary",
        ):
            try:
                bankroll_id = bankroll_options[
                    selected_adjust_bankroll
                ]

                result = execute_adjustment(
                    bankroll_id=bankroll_id,
                    amount=adjustment_amount,
                    description=(
                        adjustment_description
                    ),
                )

                load_bankrolls.clear()

                st.success(
                    "Ajuste realizado com sucesso."
                )

                st.write(
                    f"Novo saldo: "
                    f"R$ "
                    f"{result['balance_after']:.2f}"
                )

            except Exception as error:
                st.error(
                    f"Erro ao ajustar banca: {error}"
                )


with tab_status:
    st.subheader("Ativar ou desativar banca")

    if not bankroll_options:
        st.warning(
            "Nenhuma banca cadastrada."
        )

    else:
        selected_status_bankroll = (
            st.selectbox(
                "Banca",
                options=list(
                    bankroll_options.keys()
                ),
                key="status_bankroll",
            )
        )

        desired_status = st.selectbox(
            "Novo status",
            options=[
                "Ativa",
                "Inativa",
            ],
        )

        confirm_status = st.checkbox(
            "Confirmo a alteração de status",
        )

        if st.button(
            "Alterar status",
            type="primary",
        ):
            try:
                if not confirm_status:
                    raise ValueError(
                        "Confirme a alteração."
                    )

                bankroll_id = bankroll_options[
                    selected_status_bankroll
                ]

                active = (
                    desired_status == "Ativa"
                )

                result = execute_status_change(
                    bankroll_id=bankroll_id,
                    active=active,
                )

                load_bankrolls.clear()

                st.success(
                    f"Banca '{result['name']}' "
                    f"definida como "
                    f"{'ativa' if result['active'] else 'inativa'}."
                )

            except Exception as error:
                st.error(
                    f"Erro ao alterar status: {error}"
                )