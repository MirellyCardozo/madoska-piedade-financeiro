from passlib.hash import pbkdf2_sha256
from database import executar

nome = "Administrador"
usuario = "admin"
senha_plana = "1234"
perfil = "admin"

senha_hash = pbkdf2_sha256.hash(senha_plana)

SQL = """
INSERT INTO usuarios (nome, usuario, senha, perfil)
VALUES (:nome, :usuario, :senha, :perfil)
ON CONFLICT (usuario) DO NOTHING;
"""

executar(
    SQL,
    {
        "nome": nome,
        "usuario": usuario,
        "senha": senha_hash,
        "perfil": perfil
    }
)

print("✅ Usuário admin criado com sucesso")
