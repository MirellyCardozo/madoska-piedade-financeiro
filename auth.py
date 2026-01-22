import streamlit as st
from sqlalchemy import create_engine, text
import bcrypt

engine = create_engine("sqlite:///madoska.db")

def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    with engine.connect() as conn:
        conn.execute(text("""
        INSERT INTO usuarios (nome, usuario, senha, perfil)
        VALUES (:nome, :usuario, :senha, :perfil)
        """), {
            "nome": nome,
            "usuario": usuario,
            "senha": senha_hash,
            "perfil": perfil
        })

def autenticar(usuario, senha):
    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
        """), {"usuario": usuario}).fetchone()

    if result:
        senha_hash = result[3].encode()
        if bcrypt.checkpw(senha.encode(), senha_hash):
            return {
                "id": result[0],
                "nome": result[1],
                "usuario": result[2],
                "perfil": result[4]
            }
    return None

def tela_login():
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state.usuario = user
            st.success(f"Bem-vinda, {user['nome']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
