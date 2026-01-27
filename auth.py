import streamlit as st
from passlib.context import CryptContext
from database import executar

# ==========================
# CONFIG
# ==========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BYTES = 72

# ==========================
# HELPERS
# ==========================

def _normalizar_senha(senha: str) -> str:
    """
    Garante que a senha não passe de 72 bytes (limite do bcrypt)
    sem quebrar caracteres UTF-8
    """
    senha_bytes = senha.encode("utf-8")

    if len(senha_bytes) <= MAX_BYTES:
        return senha

    # corta em bytes sem quebrar caractere
    cortado = senha_bytes[:MAX_BYTES]
    return cortado.decode("utf-8", errors="ignore")


def gerar_hash(senha: str) -> str:
    senha = _normalizar_senha(senha)
    return pwd_context.hash(senha)


def verificar_senha(senha_digitada: str, senha_banco: str) -> bool:
    senha_digitada = _normalizar_senha(senha_digitada)

    try:
        # tenta como bcrypt
        return pwd_context.verify(senha_digitada, senha_banco)
    except:
        # fallback: senha antiga em texto puro
        return senha_digitada == senha_banco


# ==========================
# LOGIN
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

        # Se a senha ainda estiver em texto puro, converte para hash
        if not senha_banco.startswith("$2"):
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
