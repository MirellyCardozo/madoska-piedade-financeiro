import streamlit as st
from datetime import date
from database import executar

def tela_lancamentos(user):
    st.title("💰 Lançamentos Financeiros")

    st.subheader("Novo Lançamento")

    data = st.date_input("Data", value=date.today())
    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    categoria = st.text_input("Categoria")
    descricao = st.text_input("Descrição")
    pagamento = st.selectbox("Forma de pagamento", ["Dinheiro", "Pix", "Cartão", "Outro"])
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    observacoes = st.text_area("Observações")

    if st.button("Salvar lançamento"):
        executar(
            """
            INSERT INTO registros
            (data, tipo, categoria, descricao, pagamento, valor, observacoes)
            VALUES
            (:data, :tipo, :categoria, :descricao, :pagamento, :valor, :obs)
            """,
            {
                "data": str(data),
                "tipo": tipo,
                "categoria": categoria,
                "descricao": descricao,
                "pagamento": pagamento,
                "valor": valor,
                "obs": observacoes
            }
        )
        st.success("Lançamento salvo")
        st.rerun()

    st.divider()
    st.subheader("Registros")

    dados = executar(
        """
        SELECT id, data, tipo, categoria, descricao, pagamento, valor
        FROM registros
        ORDER BY data DESC
        """,
        fetchall=True
    )

    if not dados:
        st.info("Nenhum lançamento registrado")
        return

    for r in dados:
        with st.expander(f"{r['data']} | {r['descricao']} | R$ {r['valor']}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🗑 Excluir", key=f"del_{r['id']}"):
                    executar(
                        "DELETE FROM registros WHERE id=:id",
                        {"id": r["id"]}
                    )
                    st.warning("Registro excluído")
                    st.rerun()

            with col2:
                st.write(f"Tipo: {r['tipo']}")
                st.write(f"Categoria: {r['categoria']}")
                st.write(f"Pagamento: {r['pagamento']}")
