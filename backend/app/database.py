"""Conexão com o MySQL (PyMySQL) via SQLAlchemy. Configuração lida do .env."""
import os
from typing import Iterator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv()


def _montar_url() -> str:
    url = os.getenv("DATABASE_URL")  # permite sobrescrever (ex.: SQLite nos testes)
    if url:
        return url
    usuario = quote_plus(os.getenv("DB_USER", "aegis"))
    senha = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "127.0.0.1")
    porta = os.getenv("DB_PORT", "3306")
    nome = os.getenv("DB_NAME", "aegis_lpr")
    return f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome}?charset=utf8mb4"


DATABASE_URL = _montar_url()

_kwargs: dict = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    _kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in DATABASE_URL or DATABASE_URL.endswith("sqlite://"):
        _kwargs["poolclass"] = StaticPool
else:
    _kwargs["pool_recycle"] = 1800

engine = create_engine(DATABASE_URL, **_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
