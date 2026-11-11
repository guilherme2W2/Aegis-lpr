from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import PapelUsuario, Usuario
from app.models.veiculo import StatusVeiculo, TipoVeiculo, Veiculo
from app.schemas.veiculo import (
    VeiculoAtualizar, VeiculoMoradorCriar, VeiculoReativar, VeiculoResposta, VeiculoVisitanteCriar,
)
from app.security import exigir_papeis, usuario_atual
from app.services import controle_acesso
from app.utils.formatacao import agora

router = APIRouter(prefix="/veiculos", tags=["Veículos"])

SUPER = PapelUsuario.SUPER_ADMIN
ADMIN = PapelUsuario.ADMIN
PORTEIRO = PapelUsuario.PORTEIRO
MORADOR = PapelUsuario.MORADOR


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Placa já cadastrada")


def _checar_placa_livre(db: Session, placa: str, ignorar_id: Optional[int] = None) -> None:
    existente = db.scalar(select(Veiculo).where(Veiculo.placa == placa))
    if existente and existente.id != ignorar_id:
        if existente.tipo == TipoVeiculo.VISITANTE and existente.status == StatusVeiculo.DESATIVADO:
            raise HTTPException(status.HTTP_409_CONFLICT, "Placa de visitante desativada: use a reativação (até 48h)")
        raise HTTPException(status.HTTP_409_CONFLICT, "Placa já cadastrada")


def _morador_valido(db: Session, morador_id: int) -> Usuario:
    morador = db.get(Usuario, morador_id)
    if morador is None or morador.papel != MORADOR or not morador.ativo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Morador não encontrado ou inativo")
    return morador


def _obter_visivel(db: Session, veiculo_id: int, usuario: Usuario) -> Veiculo:
    """Carrega o veículo respeitando o escopo do perfil (404 para não vazar existência)."""
    veiculo = db.get(Veiculo, veiculo_id)
    if veiculo is not None:
        if usuario.papel == MORADOR and veiculo.dono_id != usuario.id:
            veiculo = None
        elif usuario.papel == PORTEIRO and veiculo.tipo != TipoVeiculo.VISITANTE:
            veiculo = None
    if veiculo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veículo não encontrado")
    return veiculo


def _exigir_visitante(veiculo: Veiculo) -> None:
    if veiculo.tipo != TipoVeiculo.VISITANTE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Operação válida apenas para veículos de visitantes")


# ----------------------------------------------------------------------------- criação
@router.post("/moradores", response_model=VeiculoResposta, status_code=status.HTTP_201_CREATED)
def cadastrar_veiculo_morador(
    dados: VeiculoMoradorCriar, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(ADMIN, SUPER)),
):
    """Carro fixo de morador (placa, modelo, cor). Admin/Super ADM."""
    _morador_valido(db, dados.dono_id)
    _checar_placa_livre(db, dados.placa)
    veiculo = Veiculo(
        placa=dados.placa, modelo=dados.modelo, cor=dados.cor, tipo=TipoVeiculo.MORADOR,
        status=StatusVeiculo.ATIVO, dono_id=dados.dono_id, criado_por_id=ator.id,
    )
    db.add(veiculo)
    _commit(db)
    db.refresh(veiculo)
    return veiculo


@router.post("/visitantes", response_model=VeiculoResposta, status_code=status.HTTP_201_CREATED)
def cadastrar_visitante(
    dados: VeiculoVisitanteCriar, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(PORTEIRO, SUPER)),
):
    """Placa temporária com duração (1h, 12h, 24h...). Limite de visitantes ativos por morador."""
    _morador_valido(db, dados.morador_id)
    _checar_placa_livre(db, dados.placa)
    limite = controle_acesso.max_visitantes_por_morador()
    if controle_acesso.contar_visitantes_ativos(db, dados.morador_id) >= limite:
        raise HTTPException(status.HTTP_409_CONFLICT, f"O morador já possui {limite} visitantes ativos")
    veiculo = Veiculo(
        placa=dados.placa, modelo=dados.modelo, cor=dados.cor, tipo=TipoVeiculo.VISITANTE,
        status=StatusVeiculo.ATIVO, dono_id=dados.morador_id, criado_por_id=ator.id,
        duracao_horas=dados.duracao_horas, expira_em=agora() + timedelta(hours=dados.duracao_horas), notas=dados.notas,
    )
    db.add(veiculo)
    _commit(db)
    db.refresh(veiculo)
    return veiculo


# ----------------------------------------------------------------------------- consulta
@router.get("", response_model=list[VeiculoResposta])
def listar_veiculos(
    tipo: Optional[TipoVeiculo] = None,
    status_veiculo: Optional[StatusVeiculo] = Query(default=None, alias="status"),
    morador_id: Optional[int] = None,
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual),
):
    """Morador: só os seus (+ 2 visitantes). Porteiro: só visitantes. Admin/Super: todos."""
    controle_acesso.desativar_expirados(db)
    consulta = select(Veiculo)
    if usuario.papel == MORADOR:
        consulta = consulta.where(Veiculo.dono_id == usuario.id)
    elif usuario.papel == PORTEIRO:
        consulta = consulta.where(Veiculo.tipo == TipoVeiculo.VISITANTE)
    if tipo:
        consulta = consulta.where(Veiculo.tipo == tipo)
    if status_veiculo:
        consulta = consulta.where(Veiculo.status == status_veiculo)
    if morador_id is not None and usuario.papel != MORADOR:
        consulta = consulta.where(Veiculo.dono_id == morador_id)
    return db.scalars(consulta.order_by(Veiculo.criado_em.desc()).limit(limite).offset(offset)).unique().all()


@router.get("/{veiculo_id}", response_model=VeiculoResposta)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    controle_acesso.desativar_expirados(db)
    return _obter_visivel(db, veiculo_id, usuario)


# ----------------------------------------------------------------------------- alteração
@router.patch("/{veiculo_id}", response_model=VeiculoResposta)
def atualizar_veiculo(
    veiculo_id: int, dados: VeiculoAtualizar, db: Session = Depends(get_db),
    ator: Usuario = Depends(exigir_papeis(ADMIN, PORTEIRO, SUPER)),
):
    """Carros fixos: Admin/Super. Visitantes: Porteiro/Super."""
    veiculo = _obter_visivel(db, veiculo_id, ator)
    fixo = veiculo.tipo == TipoVeiculo.MORADOR
    if fixo and ator.papel == PORTEIRO or (not fixo and ator.papel == ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Perfil sem permissão para este tipo de veículo")
    mudancas = dados.model_dump(exclude_unset=True)
    if "status" in mudancas:
        if not fixo:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Use /saida ou /reativar para visitantes")
        novo = mudancas.pop("status")
        if novo is not None and novo != veiculo.status:
            veiculo.status = novo
            veiculo.desativado_em = agora() if novo == StatusVeiculo.DESATIVADO else None
    if mudancas.get("placa"):
        _checar_placa_livre(db, mudancas["placa"], ignorar_id=veiculo.id)
    for campo, valor in mudancas.items():
        if valor is not None:
            setattr(veiculo, campo, valor)
    _commit(db)
    db.refresh(veiculo)
    return veiculo


@router.post("/{veiculo_id}/saida", response_model=VeiculoResposta)
def registrar_saida(veiculo_id: int, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(PORTEIRO, SUPER))):
    """Saída do visitante: a placa passa para DESATIVADO (e é apagada após 48h)."""
    veiculo = _obter_visivel(db, veiculo_id, ator)
    _exigir_visitante(veiculo)
    if veiculo.status == StatusVeiculo.ATIVO:
        controle_acesso.desativar_veiculo(veiculo)
        db.commit()
        db.refresh(veiculo)
    return veiculo


@router.post("/{veiculo_id}/reativar", response_model=VeiculoResposta)
def reativar_visitante(
    veiculo_id: int, dados: VeiculoReativar = VeiculoReativar(), db: Session = Depends(get_db),
    ator: Usuario = Depends(exigir_papeis(PORTEIRO, SUPER)),
):
    """Reativa placa temporária desativada há até 48h."""
    veiculo = _obter_visivel(db, veiculo_id, ator)
    _exigir_visitante(veiculo)
    try:
        return controle_acesso.reativar_visitante(db, veiculo, dados.duracao_horas)
    except ValueError as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, str(erro))


@router.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_veiculo(veiculo_id: int, db: Session = Depends(get_db), ator: Usuario = Depends(exigir_papeis(ADMIN, SUPER))):
    """Remove carro fixo (Admin/Super). Visitantes só o Super ADM; o histórico de acessos é preservado."""
    veiculo = _obter_visivel(db, veiculo_id, ator)
    if veiculo.tipo == TipoVeiculo.VISITANTE and ator.papel != SUPER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Visitantes são removidos automaticamente após 48h desativados")
    controle_acesso.remover_veiculo(db, veiculo)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
