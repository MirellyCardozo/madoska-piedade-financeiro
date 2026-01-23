import hashlib
from database import executar


# ==========================
# FUNÇÕES DE SEGURANÇA
# ==========================
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def verificar_senha(senha_digitada, senha_banco):
    return hash_senha(senha_digitada) == senha_banco


# ==========================
# AUTENTICAÇÃO
# ==========================
def autenticar(usuario, senha):
    result = executar("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
    """, {"usuario": usuario}).fetchone()

    if not result:
        return None

    senha_banco = result[3]

    if verificar_senha(senha, senha_banco):
        return {
            "id": result[0],
            "nome": result[1],
            "usuario": result[2],
            "perfil": result[4]
        }

    return None


# ==========================
# CRIAR USUÁRIO
# ==========================
def criar_usuario(nome, usuario, senha, perfil="user"):
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


# ==========================
# TROCAR SENHA
# ==========================
def trocar_senha(usuario, nova_senha):
    senha_hash = hash_senha(nova_senha)

    executar("""
        UPDATE usuarios
        SET senha = :senha
        WHERE usuario = :usuario
    """, {
        "senha": senha_hash,
        "usuario": usuario
    })
