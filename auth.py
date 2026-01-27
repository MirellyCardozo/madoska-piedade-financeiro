from passlib.context import CryptContext
from database import executar

# ==========================
# CONFIGURAÇÃO DE HASH
# ==========================
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ==========================
# FUNÇÕES DE SENHA
# ==========================
def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_digitada, senha_hash)

# ==========================
# CRIAR USUÁRIO
# ==========================
def criar_usuario(nome, usuario, senha, perfil="admin"):
    senha_hash = hash_senha(senha)

    sql = """
    INSERT INTO usuarios (nome, usuario, senha, perfil)
    VALUES (:nome, :usuario, :senha, :perfil)
    """

    executar(sql, {
        "nome": nome,
        "usuario": usuario,
        "senha": senha_hash,
        "perfil": perfil
    })

# ==========================
# AUTENTICAR
# ==========================
def autenticar(usuario, senha):
    sql = """
    SELECT id, nome, usuario, senha, perfil
    FROM usuarios
    WHERE usuario = :usuario
    """

    result = executar(sql, {
        "usuario": usuario
    }).fetchone()

    if not result:
        return None

    senha_hash = result[3]

    if verificar_senha(senha, senha_hash):
        return {
            "id": result[0],
            "nome": result[1],
            "usuario": result[2],
            "perfil": result[4]
        }

    return None
