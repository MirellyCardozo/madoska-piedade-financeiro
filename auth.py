import bcrypt
from database import executar

# =========================
# CRIAR USUÁRIO
# =========================
def criar_usuario(nome, usuario, senha, perfil):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

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


# =========================
# AUTENTICAR LOGIN
# =========================
def autenticar(usuario, senha):
    sql = """
    SELECT id, nome, usuario, senha, perfil
    FROM usuarios
    WHERE usuario = :usuario
    """

    result = executar(sql, {"usuario": usuario}).fetchone()

    if not result:
        return None

    senha_banco = result[3]

    # Se senha no banco ainda não for hash, converte automaticamente
    if not senha_banco.startswith("$2b$"):
        novo_hash = bcrypt.hashpw(senha_banco.encode(), bcrypt.gensalt()).decode()
        executar(
            "UPDATE usuarios SET senha = :senha WHERE id = :id",
            {"senha": novo_hash, "id": result[0]}
        )
        senha_banco = novo_hash

    # Verifica senha digitada
    if bcrypt.checkpw(senha.encode(), senha_banco.encode()):
        return {
            "id": result[0],
            "nome": result[1],
            "usuario": result[2],
            "perfil": result[4]
        }

    return None


# =========================
# TROCAR SENHA
# =========================
def trocar_senha(usuario, nova_senha):
    senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

    executar(
        "UPDATE usuarios SET senha = :senha WHERE usuario = :usuario",
        {"senha": senha_hash, "usuario": usuario}
    )
