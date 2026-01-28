import streamlit as st
from datetime import date
from database import executar

# Categorias fixas
CATEGORIAS = [
    "Aluguel",
    "Energia",
    "Água",
    "Internet",
    "Funcionários",
    "Fornecedores",
    "Impostos",
    "Outros"
]

# Formas de pagamento (BOLETO VOLTOU)
PAGAMENTOS = [
    "Dinheiro",
    "Cartão Débito",
    "Cartão Crédito",
    "PIX",
    "Boleto",
    "Transferência"
]


def tela_lancamentos(user):
    st.title("💰 Lançamentos Financeiros")

    # ======================
    # NOVO LANÇAMENTO
    # ======================
    st.subheader("Novo lançamento")

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data", value=date.today())
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        categoria = st.selectbox("Categoria", CATEGORIAS)

    with col2:
        descricao = st.text_input("Descrição")
        pagamento = st.selectbox("Forma de pagamento", PAGAMENTOS)
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

    observacoes = st.text_area("Observações")

    if st.button("Salvar lançamento"):
        if valor > 0 and descricao:
            executar(
                """
                INSERT INTO registros
                (data, tipo, descricao, categoria, pagamento, valor, observacoes)
                VALUES
                (:data, :tipo, :descricao, :categoria, :pagamento, :valor, :observacoes)
                """,
                {
                    "data": data,
                    "tipo": tipo,
                    "descricao": descricao,
                    "categoria": categoria,
                    "pagamento": pagamento,
                    "valor": valor,
                    "observacoes": observacoes
                }
            )
            st.success("Lançamento salvo com sucesso")
            st.rerun()
        else:
            st.warning("Preencha descrição e valor")

    # ======================
    # LISTAGEM
    # ======================
    st.divider()
    st.subheader("Lançamentos registrados")

    registros = executar(
        """
        SELECT id, data, tipo, descricao, categoria, pagamento, valor
        FROM registros
        ORDER BY data DESC
        """,
        fetchall=True
    )

    if not registros:
        st.info("Nenhum lançamento registrado")
        return

    for r in registros:
        with st.expander(f"{r['data']} | {r['descricao']} | R$ {float(r['valor']):.2f}"):
            st.write(f"Tipo: {r['tipo']}")
            st.write(f"Categoria: {r['categoria']}")
            st.write(f"Pagamento: {r['pagamento']}")

            if st.button("🗑 Excluir", key=f"del_reg_{r['id']}"):
                executar(
                    "DELETE FROM registros WHERE id = :id",
                    {"id": r["id"]}
                )
                st.warning("Registro removido")
                st.rerun()
