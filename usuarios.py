import streamlit as st
from sqlalchemy import text
from database import engine
from auth import gerar_hash


def tela_usuarios():
    st.title("👥 Gerenciamento de Usuários")

    with st.expander("➕ Cadastrar novo usuário"):
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        perfil = st.selectbox("Perfil", ["admin", "usuario"])

        if st.button("Cadastrar"):
            if not nome or not usuario or not senha:
                st.error("Preencha todos os campos.")
                return

            senha_hash = gerar_hash(senha)

            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO usuarios (nome, usuario, senha, perfil)
                        VALUES (:nome, :usuario, :senha, :perfil)
                    """),
                    {
                        "nome": nome,
                        "usuario": usuario,
                        "senha": senha_hash,
                        "perfil": perfil
                    }
                )

            st.success("Usuário cadastrado com sucesso!")

    st.divider()
    st.subheader("📋 Usuários cadastrados")

    with engine.begin() as conn:
        result = conn.execute(text("SELECT id, nome, usuario, perfil FROM usuarios"))
        dados = result.fetchall()

    if not dados:
        st.info("Nenhum usuário cadastrado.")
        return

    for u in dados:
        col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
        col1.write(u.nome)
        col2.write(u.usuario)
        col3.write(u.perfil)

        if col4.button("🗑️", key=f"del_{u.id}"):
            with engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM usuarios WHERE id = :id"),
                    {"id": u.id}
                )
            st.experimental_rerun()
