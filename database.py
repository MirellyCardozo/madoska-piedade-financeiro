import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def executar(query, params=None, fetchone=False, fetchall=False):
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})

        if fetchone:
            row = result.fetchone()
            return dict(row._mapping) if row else None

        if fetchall:
            return [dict(r._mapping) for r in result.fetchall()]

        return None
