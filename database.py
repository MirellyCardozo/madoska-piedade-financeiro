import streamlit as st
from sqlalchemy import create_engine, text

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

def criar_tabelas():
    # Supabase já tem as tabelas
    pass

def executar(sql, params=None):
    with engine.begin() as conn:
        if params:
            return conn.execute(text(sql), params)
        return conn.execute(text(sql))
