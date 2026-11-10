from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.usuario import PapelUsuario
from app.services import validacao


class UsuarioCriar(BaseModel):
    nome_completo: str = Field(min_length=3, max_length=150)
    email: str
    cpf: str
    unidade: str = Field(min_length=1, max_length=30)
    telefone: str
    papel: PapelUsuario = PapelUsuario.MORADOR

    @field_validator("nome_completo")
    @classmethod
    def _nome(cls, v):
        return validacao.validar_nome_completo(v)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return validacao.validar_email(v)

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, v):
        return validacao.validar_cpf(v)

    @field_validator("telefone")
    @classmethod
    def _telefone(cls, v):
        return validacao.validar_telefone(v)


class UsuarioAtualizar(BaseModel):
    nome_completo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    email: Optional[str] = None
    cpf: Optional[str] = None
    unidade: Optional[str] = Field(default=None, min_length=1, max_length=30)
    telefone: Optional[str] = None
    papel: Optional[PapelUsuario] = None
    ativo: Optional[bool] = None

    @field_validator("nome_completo")
    @classmethod
    def _nome(cls, v):
        return v if v is None else validacao.validar_nome_completo(v)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return v if v is None else validacao.validar_email(v)

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, v):
        return v if v is None else validacao.validar_cpf(v)

    @field_validator("telefone")
    @classmethod
    def _telefone(cls, v):
        return v if v is None else validacao.validar_telefone(v)


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str
    email: str
    cpf: str  # mascarado (LGPD) exceto para Admin/Super ADM
    unidade: str
    telefone: str
    papel: PapelUsuario
    ativo: bool
    primeiro_acesso: bool
    criado_em: datetime


class UsuarioCriadoResposta(UsuarioResposta):
    email_enviado: bool


class MoradorResumo(BaseModel):
    """Dados mínimos para o porteiro escolher o morador ao cadastrar um visitante."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str
    unidade: str
