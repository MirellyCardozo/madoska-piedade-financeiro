from database import executar
from passlib.hash import pbkdf2_sha256

def autenticar(usuario, senha):
    user = executar(
        "SELECT id, nome, usuario, senha, perfil FROM usuarios WHERE usuario = :u",
        {"u": usuario},
        fetchone=True
    )

    if not user:
        return None

    if pbkdf2_sha256.verify(senha, user[3]):
        return {
            "id": user[0],
            "nome": user[1],
            "usuario": user[2],
            "perfil": user[4]
        }

    return None
