import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# =============================
# CONEXÃO
# =============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido nas variáveis de ambiente")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(bind=engine)

# =============================
# EXECUTOR UNIVERSAL
# =============================

def executar(sql, params=None, fetchone=False, fetchall=False):
    with engine.begin() as conn:
        result = conn.execute(text(sql), params or {})

        if fetchone:
            row = result.fetchone()
            return tuple(row) if row else None

        if fetchall:
            rows = result.fetchall()
            return [tuple(r) for r in rows]

        return None

# =============================
# CRIAR TABELAS (OPCIONAL)
# =============================

def criar_tabelas():
    executar("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL
    )
    """)

    executar("""
    CREATE TABLE IF NOT EXISTS gastos (
        id SERIAL PRIMARY KEY,
        data DATE NOT NULL,
        categoria TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor NUMERIC NOT NULL
    )
    """)
