import hashlib
from database import executar

def gerar_hash(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def autenticar(usuario, senha):
    user = executar(
        """
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
        """,
        {"usuario": usuario},
        fetchone=True
    )

    if not user:
        return None

    if gerar_hash(senha) == user["senha"]:
        return user

    return None

def criar_usuario(nome, usuario, senha, perfil):
    executar(
        """
        INSERT INTO usuarios (nome, usuario, senha, perfil)
        VALUES (:nome, :usuario, :senha, :perfil)
        """,
        {
            "nome": nome,
            "usuario": usuario,
            "senha": gerar_hash(senha),
            "perfil": perfil
        }
    )
