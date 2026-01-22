import os
import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime
import pandas as pd

# -----------------------------
# BANCO AUTOMÁTICO
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "madoska.db")
engine = create_engine(f"sqlite:///{DB_FILE}")

# -----------------------------
# CATEGORIAS FIXAS
# -----------------------------
CATEGORIAS = ["Sorvetes", "Descartáveis", "Guloseimas", "Limpeza"]

# -----------------------------
# TELA ESTOQUE
# -----------------------------
def tela_estoque():
    st.subheader("📦 Controle de Estoque")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ver Estoque",
        "➕ Cadastrar Produto",
        "🔄 Atualizar Quantidade",
        "✏️ Editar / 🗑️ Excluir"
    ])

    # -----------------------------
    # VER ESTOQUE
    # -----------------------------
    with tab1:
        df = pd.read_sql("SELECT * FROM estoque ORDER BY categoria, produto", engine)

        if df.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            def alerta(row):
                return "⚠️ ESTOQUE BAIXO" if row["quantidade"] <= row["minimo"] else ""

            df["Status"] = df.apply(alerta, axis=1)
            st.dataframe(df, use_container_width=True)

    # -----------------------------
    # CADASTRAR PRODUTO
    # -----------------------------
    with tab2:
        produto = st.text_input("Nome do produto")
        categoria = st.selectbox("Categoria", CATEGORIAS)
        quantidade = st.number_input("Quantidade inicial", min_value=0.0)
        unidade = st.text_input("Unidade (litros, unidades, caixas...)")
        minimo = st.number_input("Estoque mínimo", min_value=0.0)

        if st.button("Cadastrar Produto"):
            if not produto or not unidade:
                st.error("Preencha o nome do produto e a unidade.")
            else:
                with engine.begin() as conn:
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
                st.success("Produto cadastrado com sucesso!")
                st.rerun()

    # -----------------------------
    # ATUALIZAR QUANTIDADE
    # -----------------------------
    with tab3:
        produtos = pd.read_sql("SELECT id, produto, quantidade, unidade FROM estoque ORDER BY produto", engine)

        if produtos.empty:
            st.info("Nenhum produto para atualizar.")
        else:
            escolha = st.selectbox(
                "Produto",
                produtos.to_dict("records"),
                format_func=lambda x: f"{x['produto']} ({x['quantidade']} {x['unidade']})"
            )

            nova_qtd = st.number_input("Nova quantidade", min_value=0.0)

            if st.button("Atualizar Quantidade"):
                with engine.begin() as conn:
                    conn.execute(text("""
                    UPDATE estoque
                    SET quantidade = :q, ultima_atualizacao = :d
                    WHERE id = :id
                    """), {
                        "q": nova_qtd,
                        "d": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "id": escolha["id"]
                    })
                st.success("Quantidade atualizada!")
                st.rerun()

    # -----------------------------
    # EDITAR / EXCLUIR
    # -----------------------------
    with tab4:
        produtos = pd.read_sql("SELECT * FROM estoque ORDER BY produto", engine)

        if produtos.empty:
            st.info("Nenhum produto para editar ou excluir.")
        else:
            escolha = st.selectbox(
                "Selecione o produto",
                produtos.to_dict("records"),
                format_func=lambda x: x["produto"]
            )

            produto_edit = st.text_input("Produto", value=escolha["produto"])
            categoria_edit = st.selectbox(
                "Categoria",
                CATEGORIAS,
                index=CATEGORIAS.index(escolha["categoria"]) if escolha["categoria"] in CATEGORIAS else 0
            )
            quantidade_edit = st.number_input("Quantidade", min_value=0.0, value=float(escolha["quantidade"]))
            unidade_edit = st.text_input("Unidade", value=escolha["unidade"])
            minimo_edit = st.number_input("Estoque mínimo", min_value=0.0, value=float(escolha["minimo"]))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Salvar Alterações"):
                    with engine.begin() as conn:
                        conn.execute(text("""
                        UPDATE estoque
                        SET produto = :p,
                            categoria = :c,
                            quantidade = :q,
                            unidade = :u,
                            minimo = :m,
                            ultima_atualizacao = :d
                        WHERE id = :id
                        """), {
                            "p": produto_edit,
                            "c": categoria_edit,
                            "q": quantidade_edit,
                            "u": unidade_edit,
                            "m": minimo_edit,
                            "d": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "id": escolha["id"]
                        })
                    st.success("Produto atualizado com sucesso!")
                    st.rerun()

            with col2:
                if st.button("🗑️ Excluir Produto"):
                    with engine.begin() as conn:
                        conn.execute(text(
                            "DELETE FROM estoque WHERE id = :id"
                        ), {"id": escolha["id"]})
                    st.warning("Produto excluído!")
                    st.rerun()
