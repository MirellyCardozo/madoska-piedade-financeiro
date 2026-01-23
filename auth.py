from database import executar
import hashlib
import bcrypt


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = hash_senha(senha)

    executar("""
        INSERT INTO usuarios (nome, usuario, senha, perfil)
        VALUES (:nome, :usuario, :senha, :perfil)
    """, {
        "nome": nome,
        "usuario": usuario,
        "senha": senha_hash,
        "perfil": perfil
    })

def autenticar(usuario, senha):
    senha_hash = hash_senha(senha)

    result = executar("""
        SELECT id, nome, usuario, perfil
        FROM usuarios
        WHERE usuario = :usuario
        AND senha = :senha
    """, {
        "usuario": usuario,
        "senha": senha_hash
    }).fetchone()

    return result
from sqlalchemy import text
import streamlit as st
from database import engine
import bcrypt


def trocar_senha(usuario, nova_senha):
    senha_hash = bcrypt.hashpw(
        nova_senha.encode(),
        bcrypt.gensalt()
    ).decode()

    with engine.begin() as conn:
        conn.execute(
            text("""
            UPDATE usuarios
            SET senha = :senha
            WHERE usuario = :usuario
            """),
            {
                "senha": senha_hash,
                "usuario": usuario
            }
        )

    return True
