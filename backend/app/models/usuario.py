import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.formatacao import agora


class PapelUsuario(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    PORTEIRO = "PORTEIRO"
    MORADOR = "MORADOR"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True)  # somente dígitos
    unidade: Mapped[str] = mapped_column(String(30))  # apto/casa
    telefone: Mapped[str] = mapped_column(String(20))
    senha_hash: Mapped[str] = mapped_column(String(255))
    papel: Mapped[PapelUsuario] = mapped_column(Enum(PapelUsuario, native_enum=False, length=20), index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    primeiro_acesso: Mapped[bool] = mapped_column(Boolean, default=True)  # força troca de senha
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora)
    ultimo_login_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
