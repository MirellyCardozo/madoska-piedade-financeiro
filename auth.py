from database import executar
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_usuario(nome, usuario, senha, perfil):
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

def autenticar(usuario, senha):
    senha_hash = hash_senha(senha)

    result = executar("""
        SELECT id, nome, usuario, perfil
        FROM usuarios
        WHERE usuario = :usuario
        AND senha = :senha
    """, {
        "usuario": usuario,
        "senha": senha_hash
    }).fetchone()

    return result
