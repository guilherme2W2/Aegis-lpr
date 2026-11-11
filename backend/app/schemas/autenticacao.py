from pydantic import BaseModel, Field, field_validator

from app.services import validacao


class LoginEntrada(BaseModel):
    email: str = Field(max_length=150)
    senha: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return v.strip().lower()


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    primeiro_acesso: bool  # True => só é possível chamar /auth/trocar-senha
    expira_em_minutos: int


class TrocarSenhaEntrada(BaseModel):
    senha_atual: str = Field(min_length=1, max_length=128)
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def _forte(cls, v):
        return validacao.validar_senha_forte(v)
