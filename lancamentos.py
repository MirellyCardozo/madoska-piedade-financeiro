import streamlit as st
from sqlalchemy import text
from database import engine
from datetime import date


def tela_lancamentos():
    st.title("💰 Lançamentos Financeiros")

    with st.expander("➕ Novo Lançamento"):
        data = st.date_input("Data", value=date.today())
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        descricao = st.text_input("Descrição")
        categoria = st.text_input("Categoria")
        pagamento = st.selectbox("Forma de pagamento", ["Dinheiro", "Pix", "Cartão", "Outro"])
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        observacoes = st.text_area("Observações")

        if st.button("Salvar"):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO registros
                        (data, tipo, descricao, categoria, pagamento, valor, observacoes)
                        VALUES
                        (:data, :tipo, :descricao, :categoria, :pagamento, :valor, :observacoes)
                    """),
                    {
                        "data": str(data),
                        "tipo": tipo,
                        "descricao": descricao,
                        "categoria": categoria,
                        "pagamento": pagamento,
                        "valor": valor,
                        "observacoes": observacoes
                    }
                )
            st.success("Lançamento salvo!")
            st.experimental_rerun()

    st.divider()
    st.subheader("📋 Registros")

    with engine.begin() as conn:
        dados = conn.execute(
            text("SELECT * FROM registros ORDER BY data DESC")
        ).fetchall()

    if not dados:
        st.info("Nenhum lançamento registrado.")
        return

    for r in dados:
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 2, 2, 1])

        col1.write(r.data)
        col2.write(r.tipo)
        col3.write(r.descricao)
        col4.write(r.categoria)
        col5.write(f"R$ {float(r.valor):.2f}")

        if col6.button("🗑️", key=f"del_reg_{r.id}"):
            with engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM registros WHERE id = :id"),
                    {"id": r.id}
                )
            st.experimental_rerun()
