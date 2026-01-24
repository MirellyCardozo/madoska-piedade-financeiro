from passlib.hash import bcrypt
from database import executar


def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = bcrypt.hash(senha)

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
    result = executar("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
    """, {
        "usuario": usuario
    }).fetchone()

    if result:
        senha_hash = result[3]

        if bcrypt.verify(senha, senha_hash):
            return {
                "id": result[0],
                "nome": result[1],
                "usuario": result[2],
                "perfil": result[4]
            }

    return None