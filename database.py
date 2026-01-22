from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///madoska.db")

def criar_tabela():
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

