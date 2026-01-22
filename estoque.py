import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine("sqlite:///madoska.db")

CATEGORIAS = ["Sorvetes", "Descartáveis", "Guloseimas", "Limpeza"]

def tela_estoque():
    st.subheader("📦 Controle de Estoque")

    tab1, tab2, tab3 = st.tabs(["📋 Ver Estoque", "➕ Cadastrar Produto", "🔄 Atualizar Quantidade"])

    with tab1:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM estoque")).fetchall()

        if rows:
            for r in rows:
                alerta = "⚠️ ESTOQUE BAIXO" if r[3] <= r[5] else ""
                st.write(f"**{r[1]}** | {r[2]} | {r[3]} {r[4]} | Mín: {r[5]} {alerta}")
        else:
            st.info("Nenhum produto cadastrado.")

    with tab2:
        produto = st.text_input("Nome do produto")
        categoria = st.selectbox("Categoria", CATEGORIAS)
        quantidade = st.number_input("Quantidade inicial", min_value=0.0)
        unidade = st.text_input("Unidade (litros, unidades, caixas...)")
        minimo = st.number_input("Estoque mínimo", min_value=0.0)

        if st.button("Cadastrar"):
            with engine.connect() as conn:
                conn.execute(text("""
                INSERT INTO estoque
                (produto, categoria, quantidade, unidade, minimo, ultima_atualizacao)
                VALUES (:p, :c, :q, :u, :m, :d)
                """), {
                    "p": produto,
                    "c": categoria,
                    "q": quantidade,
                    "u": unidade,
                    "m": minimo,
                    "d": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
            st.success("Produto cadastrado!")

    with tab3:
        with engine.connect() as conn:
            produtos = conn.execute(text("SELECT id, produto, quantidade FROM estoque")).fetchall()

        if produtos:
            escolha = st.selectbox("Produto", produtos, format_func=lambda x: x[1])
            nova_qtd = st.number_input("Nova quantidade", min_value=0.0)

            if st.button("Atualizar"):
                with engine.connect() as conn:
                    conn.execute(text("""
                    UPDATE estoque
                    SET quantidade = :q, ultima_atualizacao = :d
                    WHERE id = :id
                    """), {
                        "q": nova_qtd,
                        "d": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "id": escolha[0]
                    })
                st.success("Quantidade atualizada!")
        else:
            st.info("Nenhum produto para atualizar.")
