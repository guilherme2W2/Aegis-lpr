import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.usuario import (
    MoradorResumo, UsuarioAtualizar, UsuarioCriadoResposta, UsuarioCriar, UsuarioResposta,
)
from app.security import exigir_papeis, gerar_senha_temporaria, hash_senha
from app.utils.formatacao import mascarar_cpf

logger = logging.getLogger("aegis.usuarios")
router = APIRouter(prefix="/usuarios", tags=["Usuários"])

PAPEIS_GESTAO = (PapelUsuario.ADMIN, PapelUsuario.SUPER_ADMIN)
PAPEIS_PRIVILEGIADOS = (PapelUsuario.ADMIN, PapelUsuario.SUPER_ADMIN)


def serializar_usuario(usuario: Usuario, visualizador: Usuario) -> UsuarioResposta:
    """LGPD: CPF completo apenas para Admin/Super ADM; demais perfis veem mascarado."""
    resposta = UsuarioResposta.model_validate(usuario)
    if visualizador.papel not in PAPEIS_GESTAO:
        resposta.cpf = mascarar_cpf(usuario.cpf)
    return resposta


def enviar_senha_temporaria(usuario: Usuario, senha: str) -> bool:
    """Envia a senha temporária por e-mail. EMAIL_MODO=console apenas registra no log (desenvolvimento)."""
    if os.getenv("EMAIL_MODO", "console").lower() == "console":
        logger.warning("[EMAIL_MODO=console] Senha temporária de %s: %s", usuario.email, senha)
        return True
    try:
        msg = EmailMessage()
        msg["Subject"] = "AEGIS-LPR - Seu acesso ao sistema"
        msg["From"] = os.getenv("SMTP_REMETENTE", "aegis@localhost")
        msg["To"] = usuario.email
        msg.set_content(
            f"Olá, {usuario.nome_completo}.\n\nSua conta no AEGIS-LPR foi criada.\n"
            f"E-mail: {usuario.email}\nSenha temporária: {senha}\n\n"
            "No primeiro acesso você será obrigado a definir uma nova senha."
        )
        with smtplib.SMTP(os.getenv("SMTP_HOST", "localhost"), int(os.getenv("SMTP_PORT", "587")), timeout=10) as smtp:
            if os.getenv("SMTP_TLS", "true").lower() == "true":
                smtp.starttls(context=ssl.create_default_context())
            if os.getenv("SMTP_USER"):
                smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD", ""))
            smtp.send_message(msg)
        return True
    except Exception:
        logger.exception("Falha ao enviar e-mail de senha temporária para %s", usuario.email)
        return False


def _garantir_unicidade(db: Session, email: Optional[str], cpf: Optional[str], ignorar_id: Optional[int] = None) -> None:
    if email:
        existente = db.scalar(select(Usuario).where(Usuario.email == email))
        if existente and existente.id != ignorar_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado")
    if cpf:
        existente = db.scalar(select(Usuario).where(Usuario.cpf == cpf))
        if existente and existente.id != ignorar_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "CPF já cadastrado")


def _obter_alvo(db: Session, usuario_id: int, ator: Usuario) -> Usuario:
    alvo = db.get(Usuario, usuario_id)
    if alvo is None or (alvo.papel == PapelUsuario.SUPER_ADMIN and ator.papel != PapelUsuario.SUPER_ADMIN):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado")
    return alvo


def _checar_permissao_sobre(alvo: Usuario, ator: Usuario) -> None:
    if alvo.papel in PAPEIS_PRIVILEGIADOS and ator.papel != PapelUsuario.SUPER_ADMIN and alvo.id != ator.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Somente o Super ADM gerencia administradores")


@router.post("", response_model=UsuarioCriadoResposta, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(*PAPEIS_GESTAO))):
    """Cadastra morador/porteiro e envia senha temporária por e-mail (troca obrigatória no 1º login)."""
    if dados.papel in PAPEIS_PRIVILEGIADOS and ator.papel != PapelUsuario.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Somente o Super ADM cria administradores")
    _garantir_unicidade(db, dados.email, dados.cpf)
    senha = gerar_senha_temporaria()
    usuario = Usuario(
        nome_completo=dados.nome_completo, email=dados.email, cpf=dados.cpf, unidade=dados.unidade,
        telefone=dados.telefone, papel=dados.papel, senha_hash=hash_senha(senha), primeiro_acesso=True, ativo=True,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail ou CPF já cadastrado")
    db.refresh(usuario)
    enviado = enviar_senha_temporaria(usuario, senha)
    base = serializar_usuario(usuario, ator)
    return UsuarioCriadoResposta(**base.model_dump(), email_enviado=enviado)


@router.get("/moradores", response_model=list[MoradorResumo])
def listar_moradores(
    busca: Optional[str] = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    ator: Usuario = Depends(exigir_papeis(PapelUsuario.PORTEIRO, *PAPEIS_GESTAO)),
):
    """Lista enxuta de moradores ativos (sem CPF/telefone) para o porteiro cadastrar visitantes."""
    consulta = select(Usuario).where(Usuario.papel == PapelUsuario.MORADOR, Usuario.ativo.is_(True))
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.where(or_(Usuario.nome_completo.ilike(termo), Usuario.unidade.ilike(termo)))
    return db.scalars(consulta.order_by(Usuario.unidade, Usuario.nome_completo).limit(200)).all()


@router.get("", response_model=list[UsuarioResposta])
def listar_usuarios(
    papel: Optional[PapelUsuario] = None,
    ativo: Optional[bool] = None,
    busca: Optional[str] = Query(default=None, max_length=100),
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    ator: Usuario = Depends(exigir_papeis(*PAPEIS_GESTAO)),
):
    consulta = select(Usuario)
    if ator.papel != PapelUsuario.SUPER_ADMIN:
        consulta = consulta.where(Usuario.papel != PapelUsuario.SUPER_ADMIN)
    if papel:
        consulta = consulta.where(Usuario.papel == papel)
    if ativo is not None:
        consulta = consulta.where(Usuario.ativo.is_(ativo))
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.where(or_(
            Usuario.nome_completo.ilike(termo), Usuario.email.ilike(termo), Usuario.unidade.ilike(termo)))
    usuarios = db.scalars(consulta.order_by(Usuario.nome_completo).limit(limite).offset(offset)).all()
    return [serializar_usuario(u, ator) for u in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioResposta)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(*PAPEIS_GESTAO))):
    return serializar_usuario(_obter_alvo(db, usuario_id, ator), ator)


@router.patch("/{usuario_id}", response_model=UsuarioResposta)
def atualizar_usuario(
    usuario_id: int, dados: UsuarioAtualizar, db: Session = Depends(get_db),
    ator: Usuario = Depends(exigir_papeis(*PAPEIS_GESTAO)),
):
    alvo = _obter_alvo(db, usuario_id, ator)
    _checar_permissao_sobre(alvo, ator)
    mudancas = dados.model_dump(exclude_unset=True)
    if mudancas.get("papel") in PAPEIS_PRIVILEGIADOS and ator.papel != PapelUsuario.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Somente o Super ADM define perfis administrativos")
    if alvo.id == ator.id and (mudancas.get("ativo") is False or ("papel" in mudancas and mudancas["papel"] != alvo.papel)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Você não pode desativar ou alterar o próprio perfil")
    _garantir_unicidade(db, mudancas.get("email"), mudancas.get("cpf"), ignorar_id=alvo.id)
    for campo, valor in mudancas.items():
        if valor is not None:
            setattr(alvo, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail ou CPF já cadastrado")
    db.refresh(alvo)
    return serializar_usuario(alvo, ator)


@router.post("/{usuario_id}/resetar-senha", response_model=UsuarioCriadoResposta)
def resetar_senha(usuario_id: int, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(*PAPEIS_GESTAO))):
    """Gera nova senha temporária (invalida tokens antigos) e exige troca no próximo login."""
    alvo = _obter_alvo(db, usuario_id, ator)
    _checar_permissao_sobre(alvo, ator)
    senha = gerar_senha_temporaria()
    alvo.senha_hash = hash_senha(senha)
    alvo.primeiro_acesso = True
    db.commit()
    enviado = enviar_senha_temporaria(alvo, senha)
    return UsuarioCriadoResposta(**serializar_usuario(alvo, ator).model_dump(), email_enviado=enviado)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_usuario(usuario_id: int, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(*PAPEIS_GESTAO))):
    """Desativação lógica (preserva o histórico de auditoria)."""
    alvo = _obter_alvo(db, usuario_id, ator)
    if alvo.id == ator.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Você não pode desativar a si mesmo")
    _checar_permissao_sobre(alvo, ator)
    alvo.ativo = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
