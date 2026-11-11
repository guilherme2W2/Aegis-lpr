import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.formatacao import agora


class TipoVeiculo(str, enum.Enum):
    MORADOR = "MORADOR"
    VISITANTE = "VISITANTE"


class StatusVeiculo(str, enum.Enum):
    ATIVO = "ATIVO"
    DESATIVADO = "DESATIVADO"


class Veiculo(Base):
    __tablename__ = "veiculos"

    id: Mapped[int] = mapped_column(primary_key=True)
    placa: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    modelo: Mapped[str] = mapped_column(String(60))
    cor: Mapped[str] = mapped_column(String(30))
    tipo: Mapped[TipoVeiculo] = mapped_column(Enum(TipoVeiculo, native_enum=False, length=20), index=True)
    status: Mapped[StatusVeiculo] = mapped_column(
        Enum(StatusVeiculo, native_enum=False, length=20), default=StatusVeiculo.ATIVO, index=True
    )
    # Morador responsável (dono do carro fixo ou morador que recebe o visitante)
    dono_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    criado_por_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    # Apenas visitantes
    duracao_horas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expira_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    desativado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora)

    dono = relationship("Usuario", foreign_keys=[dono_id], lazy="joined")

    @property
    def dono_nome(self) -> Optional[str]:
        return self.dono.nome_completo if self.dono else None

    @property
    def dono_unidade(self) -> Optional[str]:
        return self.dono.unidade if self.dono else None
