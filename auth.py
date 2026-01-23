import streamlit as st
import bcrypt
from database import executar

# ==========================
# CRIAR USUÁRIO
# ==========================
def criar_usuario(nome, usuario, senha, perfil="admin"):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    executar("""
        INSERT INTO usuarios (nome, usuario, senha, perfil)
        VALUES (:nome, :usuario, :senha, :perfil)
    """, {
        "nome": nome,
        "usuario": usuario,
        "senha": senha_hash,
        "perfil": perfil
    })

# ==========================
# AUTENTICAR LOGIN
# ==========================
def autenticar(usuario, senha_digitada):
    result = executar("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
    """, {
        "usuario": usuario
    }).fetchone()

    if not result:
        return None

    senha_hash = result[3].encode()

    if bcrypt.checkpw(senha_digitada.encode(), senha_hash):
        return {
            "id": result[0],
            "nome": result[1],
            "usuario": result[2],
            "perfil": result[4]
        }

    return None

# ==========================
# TROCAR SENHA
# ==========================
def trocar_senha(usuario, nova_senha):
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

    executar("""
        UPDATE usuarios
        SET senha = :senha
        WHERE usuario = :usuario
    """, {
        "senha": nova_hash,
        "usuario": usuario
    })
