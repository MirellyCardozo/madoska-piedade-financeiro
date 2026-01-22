from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///madoska.db")

def criar_tabelas():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo TEXT,
            descricao TEXT,
            categoria TEXT,
            pagamento TEXT,
            valor REAL,
            observacoes TEXT
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            usuario TEXT UNIQUE,
            senha TEXT,
            perfil TEXT
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            categoria TEXT,
            quantidade REAL,
            unidade TEXT,
            minimo REAL,
            ultima_atualizacao TEXT
        )
        """))
