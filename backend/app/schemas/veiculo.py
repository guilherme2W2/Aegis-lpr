from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.veiculo import StatusVeiculo, TipoVeiculo
from app.services import validacao


class _VeiculoBase(BaseModel):
    placa: str
    modelo: str = Field(min_length=1, max_length=60)
    cor: str = Field(min_length=1, max_length=30)

    @field_validator("placa")
    @classmethod
    def _placa(cls, v):
        return validacao.validar_placa_entrada(v)


class VeiculoMoradorCriar(_VeiculoBase):
    dono_id: int  # morador proprietário do veículo


class VeiculoVisitanteCriar(_VeiculoBase):
    morador_id: int  # morador que está recebendo a visita
    duracao_horas: int = Field(ge=1, le=168, description="Ex.: 1 (1h), 12 (12h), 24 (1 dia)")
    notas: Optional[str] = Field(default=None, max_length=500)


class VeiculoAtualizar(BaseModel):
    placa: Optional[str] = None
    modelo: Optional[str] = Field(default=None, min_length=1, max_length=60)
    cor: Optional[str] = Field(default=None, min_length=1, max_length=30)
    notas: Optional[str] = Field(default=None, max_length=500)
    status: Optional[StatusVeiculo] = None  # somente carros fixos

    @field_validator("placa")
    @classmethod
    def _placa(cls, v):
        return v if v is None else validacao.validar_placa_entrada(v)


class VeiculoReativar(BaseModel):
    duracao_horas: Optional[int] = Field(default=None, ge=1, le=168)


class VeiculoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    modelo: str
    cor: str
    tipo: TipoVeiculo
    status: StatusVeiculo
    dono_id: int
    dono_nome: Optional[str] = None
    dono_unidade: Optional[str] = None
    duracao_horas: Optional[int] = None
    expira_em: Optional[datetime] = None
    desativado_em: Optional[datetime] = None
    notas: Optional[str] = None
    criado_em: datetime
