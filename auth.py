from database import executar

def autenticar(usuario, senha):
    query = """
    SELECT id, nome, usuario, senha, perfil
    FROM usuarios
    WHERE usuario = :usuario
      AND senha = :senha
    """
    return executar(
        query,
        {"usuario": usuario, "senha": senha},
        fetchone=True
    )
