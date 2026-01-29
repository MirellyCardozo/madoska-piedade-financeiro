import streamlit as st
import pandas as pd
from database import executar
from passlib.hash import pbkdf2_sha256

def tela_usuarios(user):
    if user["perfil"] != "admin":
        st.error("Acesso restrito ao administrador")
        return

    st.title("👤 Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "usuario"])

    if st.button("Criar usuário"):
        hash_senha = pbkdf2_sha256.hash(senha)

        executar("""
            INSERT INTO usuarios (nome, usuario, senha, perfil)
            VALUES (:n, :u, :s, :p)
        """, {
            "n": nome,
            "u": usuario,
            "s": hash_senha,
            "p": perfil
        })
        st.success("Usuário criado!")
        st.rerun()

    rows = executar("""
        SELECT id, nome, usuario, perfil
        FROM usuarios
        ORDER BY nome
    """, fetchall=True)

    if rows:
        df = pd.DataFrame(rows, columns=[
            "ID", "Nome", "Usuário", "Perfil"
        ])
        st.dataframe(df, use_container_width=True)
