from passlib.hash import pbkdf2_sha256
from database import executar

def autenticar(usuario, senha):
    user = executar(
        "SELECT id, nome, usuario, senha, perfil FROM usuarios WHERE usuario = :u",
        {"u": usuario},
        fetchone=True
    )

    if user and pbkdf2_sha256.verify(senha, user.senha):
        return {
            "id": user.id,
            "nome": user.nome,
            "usuario": user.usuario,
            "perfil": user.perfil
        }

    return None
