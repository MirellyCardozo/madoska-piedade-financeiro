import streamlit as st
from sqlalchemy import text
from passlib.hash import pbkdf2_sha256
from database import engine


def login():
    st.title("Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, senha
                    FROM usuarios
                    WHERE usuario = :usuario
                """),
                {"usuario": usuario}
            ).fetchone()

        if result and pbkdf2_sha256.verify(senha, result.senha):
            st.session_state["usuario_id"] = result.id
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos")
