import streamlit as st
from passlib.hash import pbkdf2_sha256
from database import executar

def tela_usuarios():
    st.header("👥 Usuários")

    with st.form("novo_usuario"):
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.form_submit_button("Cadastrar"):
            executar(
                """
                INSERT INTO usuarios (nome, usuario, senha)
                VALUES (:n, :u, :s)
                """,
                {
                    "n": nome,
                    "u": usuario,
                    "s": pbkdf2_sha256.hash(senha)
                }
            )
            st.success("Usuário criado")
            st.rerun()
