import streamlit as st
from passlib.context import CryptContext
from sqlalchemy import text
from database import executar

# Configuração do hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================
# HASH E VERIFICAÇÃO
# ==========================

def gerar_hash(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_digitada: str, senha_banco: str) -> bool:
    """
    Aceita:
    - Senha em hash bcrypt
    - Senha antiga em texto puro
    Se for texto puro, converte para hash automaticamente
    """
    try:
        # Tenta como hash
        return pwd_context.verify(senha_digitada, senha_banco)
    except:
        # Se falhar, tenta como texto puro
        return senha_digitada == senha_banco


# ==========================
# AUTENTICAÇÃO
# ==========================

def autenticar(usuario, senha):
    result = executar("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
    """, {"usuario": usuario}).fetchone()

    if not result:
        return None

    user_id, nome, usuario_db, senha_banco, perfil = result

    if verificar_senha(senha, senha_banco):
        # Se a senha estava em texto puro, converte para hash
        if not senha_banco.startswith("$2b$"):
            novo_hash = gerar_hash(senha)
            executar("""
                UPDATE usuarios
                SET senha = :senha
                WHERE id = :id
            """, {"senha": novo_hash, "id": user_id})

        return {
            "id": user_id,
            "nome": nome,
            "usuario": usuario_db,
            "perfil": perfil
        }

    return None


# ==========================
# CRIAR USUÁRIO
# ==========================

def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = gerar_hash(senha)

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
# TROCAR SENHA
# ==========================

def trocar_senha(usuario, nova_senha):
    senha_hash = gerar_hash(nova_senha)

    executar("""
        UPDATE usuarios
        SET senha = :senha
        WHERE usuario = :usuario
    """, {
        "senha": senha_hash,
        "usuario": usuario
    })
