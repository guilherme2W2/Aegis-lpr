import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.formatacao import agora


class ResultadoAcesso(str, enum.Enum):
    LIBERADO = "LIBERADO"
    NEGADO = "NEGADO"


class OrigemAcesso(str, enum.Enum):
    AUTOMATICO = "AUTOMATICO"  # leitura LPR
    MANUAL = "MANUAL"  # porteiro forçou a abertura


class Acesso(Base):
    """Log de auditoria de toda tentativa de acesso (liberada ou negada)."""

    __tablename__ = "acessos"

    id: Mapped[int] = mapped_column(primary_key=True)
    placa: Mapped[str] = mapped_column(String(10), index=True)  # "ILEGIVEL"/"MANUAL" quando não há placa
    # Sem FK com cascade: o job de limpeza apaga o veículo e o log permanece (veiculo_id vira NULL)
    veiculo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("veiculos.id"), nullable=True)
    morador_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    operador_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    resultado: Mapped[ResultadoAcesso] = mapped_column(Enum(ResultadoAcesso, native_enum=False, length=20), index=True)
    origem: Mapped[OrigemAcesso] = mapped_column(Enum(OrigemAcesso, native_enum=False, length=20), index=True)
    motivo: Mapped[str] = mapped_column(String(255))
    confianca: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rele_acionado: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora, index=True)

    operador = relationship("Usuario", foreign_keys=[operador_id], lazy="joined")

    @property
    def operador_nome(self) -> Optional[str]:
        return self.operador.nome_completo if self.operador else None
