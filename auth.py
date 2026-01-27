import hashlib
from database import executar

# ==========================
# HELPERS
# ==========================

def gerar_hash(senha: str) -> str:
    """
    Gera hash SHA256 da senha
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def verificar_senha(senha_digitada: str, senha_banco: str) -> bool:
    """
    Compara senha digitada com hash salvo no banco
    Também aceita senha antiga salva em texto puro
    """
    hash_digitado = gerar_hash(senha_digitada)

    # Caso antigo: senha salva sem hash
    if senha_banco == senha_digitada:
        return True

    return hash_digitado == senha_banco


# ==========================
# LOGIN
# ==========================

def autenticar(usuario, senha):
    result = executar("""
        SELECT id, nome, usuario, senha, perfil
        FROM usuarios
        WHERE usuario = :usuario
    """, {"usuario": usuario}).fetchone()

    if not result:
        return None

    user_id, nome, usuario_db, senha_banco, perfil = result

    if verificar_senha(senha, senha_banco):

        # Atualiza senha antiga em texto puro para hash
        if len(senha_banco) < 64:
            novo_hash = gerar_hash(senha)
            executar("""
                UPDATE usuarios
                SET senha = :senha
                WHERE id = :id
            """, {"senha": novo_hash, "id": user_id})

        return {
            "id": user_id,
            "nome": nome,
            "usuario": usuario_db,
            "perfil": perfil
        }

    return None


# ==========================
# CRIAR USUÁRIO
# ==========================

def criar_usuario(nome, usuario, senha, perfil):
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
# TROCAR SENHA
# ==========================

def trocar_senha(usuario, nova_senha):
    senha_hash = gerar_hash(nova_senha)

    executar("""
        UPDATE usuarios
        SET senha = :senha
        WHERE usuario = :usuario
    """, {
        "senha": senha_hash,
        "usuario": usuario
    })
