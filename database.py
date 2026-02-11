import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não encontrada no .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

def executar(sql, params=None, fetchall=False, fetchone=False):
    with engine.begin() as conn:
        result = conn.execute(text(sql), params or {})
        if fetchall:
            return result.fetchall()
        if fetchone:
            return result.fetchone()
        return None
