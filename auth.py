from database import executar
from passlib.hash import pbkdf2_sha256

def autenticar(usuario, senha):
    query = """
    SELECT id, nome, usuario, senha, perfil
    FROM usuarios
    WHERE usuario = :usuario
    """
    user = executar(query, {"usuario": usuario}, fetchone=True)

    if not user:
        return None

    senha_hash = user[3]

    if pbkdf2_sha256.verify(senha, senha_hash):
        return {
            "id": user[0],
            "nome": user[1],
            "usuario": user[2],
            "perfil": user[4]
        }

    return None
