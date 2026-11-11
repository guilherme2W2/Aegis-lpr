from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.routers.usuarios import serializar_usuario
from app.schemas.autenticacao import LoginEntrada, TokenSaida, TrocarSenhaEntrada
from app.schemas.usuario import UsuarioResposta
from app.security import (
    criar_token_para_usuario, hash_senha, limpar_falhas, registrar_falha, usuario_atual,
    usuario_primeiro_acesso, verificar_bloqueio, verificar_senha,
)
from app.utils.formatacao import agora

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenSaida)
def login(dados: LoginEntrada, request: Request, db: Session = Depends(get_db)):
    """Se `primeiro_acesso` vier true, o token só serve para /auth/trocar-senha."""
    chave = f"{dados.email}|{request.client.host if request.client else '-'}"
    verificar_bloqueio(chave)
    usuario = db.scalar(select(Usuario).where(Usuario.email == dados.email))
    if usuario is None or not usuario.ativo or not verificar_senha(dados.senha, usuario.senha_hash):
        registrar_falha(chave)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciais inválidas")
    limpar_falhas(chave)
    usuario.ultimo_login_em = agora()
    db.commit()
    token, minutos = criar_token_para_usuario(usuario)
    return TokenSaida(access_token=token, primeiro_acesso=usuario.primeiro_acesso, expira_em_minutos=minutos)


@router.post("/trocar-senha", response_model=TokenSaida)
def trocar_senha(dados: TrocarSenhaEntrada, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_primeiro_acesso)):
    """Obrigatória no primeiro acesso; também serve para troca voluntária. Devolve um novo token."""
    if not verificar_senha(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Senha atual incorreta")
    if dados.senha_atual == dados.nova_senha:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A nova senha deve ser diferente da atual")
    usuario.senha_hash = hash_senha(dados.nova_senha)
    usuario.primeiro_acesso = False
    db.commit()
    token, minutos = criar_token_para_usuario(usuario)
    return TokenSaida(access_token=token, primeiro_acesso=False, expira_em_minutos=minutos)


@router.get("/me", response_model=UsuarioResposta)
def meus_dados(usuario: Usuario = Depends(usuario_atual)):
    return serializar_usuario(usuario, usuario)
