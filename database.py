import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def executar(sql, params=None):
    with engine.begin() as conn:
        return conn.execute(text(sql), params or {})
