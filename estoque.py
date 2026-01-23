import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "madoska.db")
engine = create_engine(f"sqlite:///{DB_FILE}")

CATEGORIAS = ["Sorvetes", "Descartáveis", "Guloseimas", "Limpeza"]

def tela_estoque():
    st.subheader("📦 Controle de Estoque")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Estoque Atual",
        "➕ Cadastrar",
        "🔄 Atualizar",
        "✏️ Editar / 🗑️ Excluir",
        "📄 Relatório por Período"
    ])

    # -------- ESTOQUE ATUAL --------
    with tab1:
        df = pd.read_sql("SELECT * FROM estoque ORDER BY categoria, produto", engine)
        if df.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            df["Status"] = df.apply(
                lambda x: "⚠️ BAIXO" if x["quantidade"] <= x["minimo"] else "OK",
                axis=1
            )
            st.dataframe(df, use_container_width=True)

    # -------- CADASTRAR --------
    with tab2:
        produto = st.text_input("Produto")
        categoria = st.selectbox("Categoria", CATEGORIAS)
        quantidade = st.number_input("Quantidade inicial", min_value=0.0)
        unidade = st.text_input("Unidade")
        minimo = st.number_input("Estoque mínimo", min_value=0.0)

        if st.button("Cadastrar"):
            if not produto or not unidade:
                st.error("Preencha o nome do produto e a unidade.")
            else:
                with engine.begin() as conn:
                    conn.execute(text("""
                    INSERT INTO estoque
                    (produto, categoria, quantidade, unidade, minimo, ultima_atualizacao)
                    VALUES (:p,:c,:q,:u,:m,:d)
                    """), {
                        "p": produto,
                        "c": categoria,
                        "q": quantidade,
                        "u": unidade,
                        "m": minimo,
                        "d": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                st.success("Produto cadastrado!")
                st.rerun()

    # -------- ATUALIZAR --------
    with tab3:
        produtos = pd.read_sql("SELECT * FROM estoque", engine)
        if produtos.empty:
            st.info("Nenhum produto disponível.")
        else:
            escolha = st.selectbox(
                "Produto",
                produtos.to_dict("records"),
                format_func=lambda x: f"{x['produto']} ({x['quantidade']} {x['unidade']})"
            )
            nova_qtd = st.number_input("Nova quantidade", min_value=0.0)

            if st.button("Atualizar Quantidade"):
                diferenca = nova_qtd - escolha["quantidade"]
                tipo = "Entrada" if diferenca > 0 else "Saída"

                with engine.begin() as conn:
                    conn.execute(text("""
                    UPDATE estoque
                    SET quantidade=:q, ultima_atualizacao=:d
                    WHERE id=:id
                    """), {
                        "q": nova_qtd,
                        "d": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "id": escolha["id"]
                    })

                    conn.execute(text("""
                    INSERT INTO estoque_historico
                    (produto_id, data, tipo, quantidade, observacao)
                    VALUES (:p,:d,:t,:q,:o)
                    """), {
                        "p": escolha["id"],
                        "d": datetime.now().strftime("%d/%m/%Y"),
                        "t": tipo,
                        "q": abs(diferenca),
                        "o": "Ajuste manual"
                    })

                st.success("Estoque atualizado!")
                st.rerun()

    # -------- EDITAR / EXCLUIR --------
    with tab4:
        produtos = pd.read_sql("SELECT * FROM estoque", engine)
        if produtos.empty:
            st.info("Nenhum produto.")
        else:
            escolha = st.selectbox(
                "Produto",
                produtos.to_dict("records"),
                format_func=lambda x: x["produto"]
            )

            nome = st.text_input("Nome", value=escolha["produto"])
            categoria = st.selectbox(
                "Categoria",
                CATEGORIAS,
                index=CATEGORIAS.index(escolha["categoria"])
            )
            unidade = st.text_input("Unidade", value=escolha["unidade"])
            minimo = st.number_input("Mínimo", value=float(escolha["minimo"]))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Salvar"):
                    with engine.begin() as conn:
                        conn.execute(text("""
                        UPDATE estoque
                        SET produto=:p, categoria=:c, unidade=:u, minimo=:m
                        WHERE id=:id
                        """), {
                            "p": nome,
                            "c": categoria,
                            "u": unidade,
                            "m": minimo,
                            "id": escolha["id"]
                        })
                    st.success("Produto atualizado!")
                    st.rerun()

            with col2:
                if st.button("🗑️ Excluir"):
                    with engine.begin() as conn:
                        conn.execute(
                            text("DELETE FROM estoque WHERE id=:id"),
                            {"id": escolha["id"]}
                        )
                    st.warning("Produto excluído!")
                    st.rerun()

    # -------- RELATÓRIO --------
    with tab5:
        st.subheader("📄 Relatório de Estoque por Período")

        inicio = st.date_input("Data inicial", value=date.today())
        fim = st.date_input("Data final", value=date.today())

        df = pd.read_sql("""
            SELECT h.data, e.produto, h.tipo, h.quantidade, h.observacao
            FROM estoque_historico h
            JOIN estoque e ON e.id = h.produto_id
            ORDER BY h.data DESC
        """, engine)

        if df.empty:
            st.info("Nenhum histórico disponível.")
        else:
            df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
            filtro = df[
                (df["data"].dt.date >= inicio) &
                (df["data"].dt.date <= fim)
            ]
            st.dataframe(filtro, use_container_width=True)
