import streamlit as st
import pandas as pd
from passlib.hash import pbkdf2_sha256
from database import executar

def tela_usuarios(user):
    if user["perfil"] != "admin":
        st.error("Acesso restrito ao administrador")
        return

    st.title("👥 Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "usuario"])

    if st.button("Criar usuário"):
        senha_hash = pbkdf2_sha256.hash(senha)

        executar(
            """
            INSERT INTO usuarios (nome, usuario, senha, perfil)
            VALUES (:nome, :usuario, :senha, :perfil)
            """,
            {
                "nome": nome,
                "usuario": usuario,
                "senha": senha_hash,
                "perfil": perfil
            }
        )
        st.success("Usuário criado")
        st.rerun()

    st.divider()

    rows = executar(
        "SELECT id, nome, usuario, perfil FROM usuarios",
        fetchall=True
    )

    df = pd.DataFrame(rows, columns=["ID", "Nome", "Usuário", "Perfil"])
    st.dataframe(df, use_container_width=True)
