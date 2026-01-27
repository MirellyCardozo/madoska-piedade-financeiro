import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime
import pytz

from database import engine

TIMEZONE = pytz.timezone("America/Sao_Paulo")

# ==========================
# BANCO
# ==========================
def criar_tabela_estoque():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS estoque (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco NUMERIC(10,2) NOT NULL,
            criado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """))

def buscar_estoque():
    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT id, nome, categoria, quantidade, preco, criado_em
            FROM estoque
            ORDER BY nome
        """)).fetchall()

    return pd.DataFrame(
        result,
        columns=["id", "nome", "categoria", "quantidade", "preco", "criado_em"]
    )

def inserir_produto(nome, categoria, quantidade, preco):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO estoque (nome, categoria, quantidade, preco)
            VALUES (:nome, :categoria, :quantidade, :preco)
        """), {
            "nome": nome,
            "categoria": categoria,
            "quantidade": quantidade,
            "preco": preco
        })

def atualizar_produto(produto_id, nome, categoria, quantidade, preco):
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE estoque
            SET nome = :nome,
                categoria = :categoria,
                quantidade = :quantidade,
                preco = :preco
            WHERE id = :id
        """), {
            "id": produto_id,
            "nome": nome,
            "categoria": categoria,
            "quantidade": quantidade,
            "preco": preco
        })

def excluir_produto(produto_id):
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM estoque
            WHERE id = :id
        """), {"id": produto_id})

# ==========================
# TELA
# ==========================
def tela_estoque():
    criar_tabela_estoque()

    st.title("📦 Controle de Estoque")

    agora = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")
    st.caption(f"Hora BR: {agora}")

    # ==========================
    # FORMULÁRIO
    # ==========================
    st.subheader("➕ Cadastrar Produto")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome do Produto")
        categoria = st.text_input("Categoria")

    with col2:
        quantidade = st.number_input("Quantidade", min_value=0, step=1)
        preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)

    if st.button("Salvar Produto"):
        if nome and categoria:
            inserir_produto(nome, categoria, quantidade, preco)
            st.success("Produto cadastrado com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha nome e categoria.")

    # ==========================
    # LISTA
    # ==========================
    df = buscar_estoque()

    if df.empty:
        st.info("Nenhum produto cadastrado.")
        return

    st.subheader("📋 Produtos em Estoque")
    st.dataframe(df, use_container_width=True)

    # ==========================
    # EDITAR / EXCLUIR
    # ==========================
    st.subheader("✏️ Editar ou Excluir Produto")

    escolha = st.selectbox(
        "Selecione um produto",
        df.to_dict("records"),
        format_func=lambda x: f"{x['id']} - {x['nome']}"
    )

    col3, col4 = st.columns(2)

    with col3:
        novo_nome = st.text_input("Nome", value=escolha["nome"])
        nova_categoria = st.text_input("Categoria", value=escolha["categoria"])

    with col4:
        nova_quantidade = st.number_input(
            "Quantidade",
            min_value=0,
            step=1,
            value=int(escolha["quantidade"])
        )
        novo_preco = st.number_input(
            "Preço (R$)",
            min_value=0.0,
            step=0.01,
            value=float(escolha["preco"])
        )

    col5, col6 = st.columns(2)

    with col5:
        if st.button("💾 Atualizar"):
            atualizar_produto(
                escolha["id"],
                novo_nome,
                nova_categoria,
                nova_quantidade,
                novo_preco
            )
            st.success("Produto atualizado!")
            st.rerun()

    with col6:
        if st.button("🗑 Excluir"):
            excluir_produto(escolha["id"])
            st.success("Produto excluído!")
            st.rerun()
