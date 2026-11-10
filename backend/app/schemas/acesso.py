from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.acesso import OrigemAcesso, ResultadoAcesso


class LeituraPlacaEntrada(BaseModel):
    """Evento de câmeras que já fazem o OCR e enviam apenas o texto da placa."""

    placa: str = Field(min_length=1, max_length=20)
    confianca: Optional[float] = Field(default=None, ge=0, le=1)


class AberturaManualEntrada(BaseModel):
    motivo: str = Field(min_length=3, max_length=200)
    placa: Optional[str] = Field(default=None, max_length=20)


class DecisaoAcessoResposta(BaseModel):
    acesso_id: int
    placa: str
    liberado: bool
    motivo: str
    rele_acionado: bool
    confianca: Optional[float] = None


class AcessoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    veiculo_id: Optional[int] = None
    morador_id: Optional[int] = None
    operador_id: Optional[int] = None
    operador_nome: Optional[str] = None
    resultado: ResultadoAcesso
    origem: OrigemAcesso
    motivo: str
    confianca: Optional[float] = None
    rele_acionado: bool
    criado_em: datetime
