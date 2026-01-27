from database import executar
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================
# HASH DE SENHA
# ==========================
def gerar_hash(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    try:
        return pwd_context.verify(senha_digitada, senha_hash)
    except:
        return False

# ==========================
# CRIAR USUÁRIO
# ==========================
def criar_usuario(nome, usuario, senha, perfil="admin"):
    senha_hash = gerar_hash(senha)

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
# AUTENTICAR
# ==========================
def autenticar(usuario, senha):
    result = executar("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
    """, {
        "usuario": usuario
    }).fetchone()

    if not result:
        return None

    senha_hash = result.senha

    if verificar_senha(senha, senha_hash):
        # RETORNA SÓ O NOME — OPÇÃO 3
        return result.nome

    return None
