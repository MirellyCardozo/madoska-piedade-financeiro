import streamlit as st
from database import executar
from datetime import date

# ==========================
# CONFIGURAÇÕES
# ==========================

CATEGORIAS = [
    "Aluguel",
    "Fornecedor",
    "Energia",
    "Internet",
    "Funcionários",
    "Impostos",
    "Manutenção",
    "Outros"
]

PAGAMENTOS = [
    "Pix",
    "Cartão",
    "Dinheiro",
    "Boleto",
    "Transferência"
]

# ==========================
# TELA LANÇAMENTOS
# ==========================

def tela_lancamentos(user):
    st.title("📒 Lançamentos Financeiros")

    # ==========================
    # FORMULÁRIO
    # ==========================
    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)

        with col1:
            data = st.date_input("Data", value=date.today())
            categoria = st.selectbox("Categoria", CATEGORIAS)

        with col2:
            pagamento = st.selectbox("Forma de Pagamento", PAGAMENTOS)
            valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01, format="%.2f")

        descricao = st.text_area("Descrição")

        salvar = st.form_submit_button("💾 Salvar lançamento")

    # ==========================
    # SALVAR NO BANCO
    # ==========================
    if salvar:
        if not descricao.strip():
            st.error("Informe a descrição")
            return

        executar(
            """
            INSERT INTO lancamentos
            (data, descricao, valor, categoria, pagamento, usuario_id)
            VALUES
            (:data, :descricao, :valor, :categoria, :pagamento, :usuario_id)
            """,
            {
                "data": str(data),
                "descricao": descricao,
                "valor": float(valor),
                "categoria": categoria,
                "pagamento": pagamento,
                "usuario_id": user["id"]
            }
        )

        st.success("✅ Lançamento salvo com sucesso")
        st.rerun()

    # ==========================
    # LISTAGEM
    # ==========================
    st.divider()
    st.subheader("📋 Lançamentos registrados")

    registros = executar(
        """
        SELECT
            id,
            data,
            descricao,
            valor,
            categoria,
            pagamento
        FROM lancamentos
        ORDER BY id DESC
        """,
        fetchall=True
    )

    if not registros:
        st.info("Nenhum lançamento cadastrado")
        return

    for r in registros:
        with st.expander(
            f"{r[1]} | {r[3]:.2f} | {r[4]} | {r[5]}"
        ):
            st.write(f"**Descrição:** {r[2]}")
            st.write(f"**Categoria:** {r[4]}")
            st.write(f"**Pagamento:** {r[5]}")
            st.write(f"**Valor:** R$ {r[3]:.2f}")

            if st.button("🗑️ Excluir", key=f"del_{r[0]}"):
                executar(
                    "DELETE FROM lancamentos WHERE id = :id",
                    {"id": r[0]}
                )
                st.success("Lançamento excluído")
                st.rerun()
