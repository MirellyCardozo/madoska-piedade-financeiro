import hashlib
from database import executar

# ==========================
# HASH SIMPLES E ESTÁVEL
# ==========================
def gerar_hash(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

# ==========================
# LOGIN
# ==========================
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

    senha_hash = gerar_hash(senha)

    if senha_hash == result["senha"]:
        return result

    return None

# ==========================
# CRIAR USUÁRIO
# ==========================
def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = gerar_hash(senha)

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
