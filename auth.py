from database import executar
from passlib.hash import pbkdf2_sha256


# =========================
# AUTENTICAÇÃO
# =========================
def autenticar(usuario, senha):
    result = executar(
        """
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
        """,
        {"usuario": usuario},
        fetchone=True
    )

    if not result:
        return None

    user = {
        "id": result[0],
        "nome": result[1],
        "usuario": result[2],
        "senha": result[3],
        "perfil": result[4]
    }

    # Verifica senha
    if pbkdf2_sha256.verify(senha, user["senha"]):
        return user

    return None


# =========================
# CRIAR USUÁRIO
# =========================
def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = pbkdf2_sha256.hash(senha)

    executar(
        """
        INSERT INTO usuarios (nome, usuario, senha, perfil)
        VALUES (:nome, :usuario, :senha, :perfil)
        """,
        {
            "nome": nome,
            "usuario": usuario,
            "senha": senha_hash,
            "perfil": perfil
        }
    )
