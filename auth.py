import streamlit as st
from sqlalchemy import create_engine, text
import bcrypt

DB_PATH = r"sqlite:///C:/Users/mirel/OneDrive/Área de Trabalho/madoska_financeiro/madoska.db"
engine = create_engine(DB_PATH)

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

def trocar_senha(usuario, senha_atual, nova_senha):
    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT senha FROM usuarios WHERE usuario = :usuario
        """), {"usuario": usuario}).fetchone()

        if not result:
            return False, "Usuário não encontrado."

        senha_hash = result[0].encode()

        if not bcrypt.checkpw(senha_atual.encode(), senha_hash):
            return False, "Senha atual incorreta."

        nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

        conn.execute(text("""
        UPDATE usuarios
        SET senha = :senha
        WHERE usuario = :usuario
        """), {
            "senha": nova_hash,
            "usuario": usuario
        })

        return True, "Senha alterada com sucesso!"

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
