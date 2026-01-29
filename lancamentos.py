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
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])

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
            INSERT INTO registros
            (data, tipo, descricao, categoria, pagamento, valor, observacoes)
            VALUES
            (:data, :tipo, :descricao, :categoria, :pagamento, :valor, '')
            """,
            {
                "data": data.strftime("%d/%m/%Y"),
                "tipo": tipo,
                "descricao": descricao,
                "categoria": categoria,
                "pagamento": pagamento,
                "valor": float(valor)
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
            tipo,
            descricao,
            valor,
            categoria,
            pagamento
        FROM registros
        ORDER BY id DESC
        """,
        fetchall=True
    )

    if not registros:
        st.info("Nenhum lançamento cadastrado")
        return

    for r in registros:
        with st.expander(
            f"{r['data']} | {r['tipo']} | R$ {float(r['valor']):.2f} | {r['categoria']}"
        ):
            st.write(f"**Descrição:** {r['descricao']}")
            st.write(f"**Categoria:** {r['categoria']}")
            st.write(f"**Pagamento:** {r['pagamento']}")
            st.write(f"**Valor:** R$ {float(r['valor']):.2f}")

            if st.button("🗑️ Excluir", key=f"del_{r['id']}"):
                executar(
                    "DELETE FROM registros WHERE id = :id",
                    {"id": r["id"]}
                )
                st.success("Lançamento excluído")
                st.rerun()
