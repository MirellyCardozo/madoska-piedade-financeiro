import hashlib
from database import executar

# =============================
# HASH SIMPLES E ESTÁVEL
# =============================

def gerar_hash(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return gerar_hash(senha_digitada) == senha_hash

# =============================
# CRIAR USUÁRIO
# =============================

def criar_usuario(nome, usuario, senha, perfil="admin"):
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

# =============================
# LOGIN
# =============================

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

    user_id, nome, usuario_db, senha_hash, perfil = result

    if verificar_senha(senha, senha_hash):
        return {
            "id": user_id,
            "nome": nome,
            "usuario": usuario_db,
            "perfil": perfil
        }

    return None
