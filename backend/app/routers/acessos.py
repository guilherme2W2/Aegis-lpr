import csv
import io
import os
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import database
from app.database import get_db
from app.models.acesso import Acesso, OrigemAcesso, ResultadoAcesso
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.acesso import (
    AberturaManualEntrada, AcessoResposta, DecisaoAcessoResposta, LeituraPlacaEntrada,
)
from app.security import exigir_papeis, usuario_atual, validar_chave_camera
from app.services import controle_acesso, reconhecimento
from app.services.validacao import normalizar_placa
from app.utils.formatacao import agora, escapar_csv, para_utc_naive

router = APIRouter(prefix="/acessos", tags=["Acessos e LPR"])

TAMANHO_MAXIMO_IMAGEM = 10 * 1024 * 1024  # 10 MB


def _resposta(decisao: controle_acesso.Decisao) -> DecisaoAcessoResposta:
    return DecisaoAcessoResposta(
        acesso_id=decisao.acesso_id, placa=decisao.placa, liberado=decisao.liberado,
        motivo=decisao.motivo, rele_acionado=decisao.rele_acionado, confianca=decisao.confianca,
    )


# ----------------------------------------------------------------------------- listener LPR (câmera)
@router.post("/lpr/placa", response_model=DecisaoAcessoResposta, dependencies=[Depends(validar_chave_camera)])
def evento_placa(dados: LeituraPlacaEntrada, db: Session = Depends(get_db)):
    """Evento de câmera que já envia o texto da placa. Header: X-Camera-Key."""
    return _resposta(controle_acesso.processar_leitura(db, dados.placa, dados.confianca))


def _processar_imagem(imagem: bytes) -> DecisaoAcessoResposta:
    try:
        leitura = reconhecimento.obter_reconhecedor().reconhecer(imagem)
    except reconhecimento.ErroImagem as erro:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(erro))
    except reconhecimento.ErroReconhecimento as erro:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(erro))
    with database.SessionLocal() as db:
        return _resposta(controle_acesso.processar_leitura(db, leitura.placa, leitura.confianca))


@router.post("/lpr/imagem", response_model=DecisaoAcessoResposta, dependencies=[Depends(validar_chave_camera)])
async def evento_imagem(request: Request):
    """Foto da câmera (corpo = bytes da imagem JPEG/PNG). Roda YOLO + EasyOCR e decide o acesso."""
    imagem = await request.body()
    if not imagem:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Corpo da requisição vazio")
    if len(imagem) > TAMANHO_MAXIMO_IMAGEM:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Imagem acima de 10 MB")
    return await run_in_threadpool(_processar_imagem, imagem)


# ----------------------------------------------------------------------------- abertura manual
@router.post("/abertura-manual", response_model=DecisaoAcessoResposta)
def abertura_manual(
    dados: AberturaManualEntrada, db: Session = Depends(get_db),
    operador: Usuario = Depends(exigir_papeis(PapelUsuario.PORTEIRO, PapelUsuario.SUPER_ADMIN)),
):
    """Falso positivo/placa suja: o porteiro força a abertura. Fica registrado 'Abertura Manual por [Nome]'."""
    return _resposta(controle_acesso.abertura_manual(db, operador, dados.motivo.strip(), dados.placa))


# ----------------------------------------------------------------------------- histórico e relatórios
def _filtros(
    inicio: Optional[datetime], fim: Optional[datetime], placa: Optional[str] = None,
    resultado: Optional[ResultadoAcesso] = None, origem: Optional[OrigemAcesso] = None,
) -> list:
    filtros = []
    if inicio:
        filtros.append(Acesso.criado_em >= para_utc_naive(inicio))
    if fim:
        filtros.append(Acesso.criado_em <= para_utc_naive(fim))
    if placa:
        filtros.append(Acesso.placa == normalizar_placa(placa))
    if resultado:
        filtros.append(Acesso.resultado == resultado)
    if origem:
        filtros.append(Acesso.origem == origem)
    return filtros


@router.get("", response_model=list[AcessoResposta])
def historico(
    data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None,
    placa: Optional[str] = Query(default=None, max_length=20),
    resultado: Optional[ResultadoAcesso] = None, origem: Optional[OrigemAcesso] = None,
    limite: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
    db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual),
):
    """Porteiro/Admin/Super: histórico geral. Morador: apenas o próprio (carros e visitantes dele)."""
    consulta = select(Acesso).where(*_filtros(data_inicio, data_fim, placa, resultado, origem))
    if usuario.papel == PapelUsuario.MORADOR:
        consulta = consulta.where(Acesso.morador_id == usuario.id)
    return db.scalars(consulta.order_by(Acesso.criado_em.desc()).limit(limite).offset(offset)).unique().all()


@router.get("/relatorio")
def relatorio(
    data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None,
    formato: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(exigir_papeis(PapelUsuario.ADMIN, PapelUsuario.SUPER_ADMIN)),
):
    """Relatório do período (padrão: últimos 30 dias). `formato=csv` exporta as linhas."""
    fim = para_utc_naive(data_fim) or agora()
    inicio = para_utc_naive(data_inicio) or fim - timedelta(days=30)
    filtros = _filtros(inicio, fim)

    if formato == "csv":
        linhas = db.scalars(select(Acesso).where(*filtros).order_by(Acesso.criado_em)).unique().all()
        saida = io.StringIO()
        escritor = csv.writer(saida)
        escritor.writerow(["id", "data_hora_utc", "placa", "resultado", "origem", "motivo", "operador", "rele_acionado"])
        for a in linhas:
            escritor.writerow([
                a.id, a.criado_em.isoformat(sep=" ", timespec="seconds"), escapar_csv(a.placa), a.resultado.value,
                a.origem.value, escapar_csv(a.motivo), escapar_csv(a.operador_nome), int(a.rele_acionado),
            ])
        return Response(
            content="\ufeff" + saida.getvalue(), media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="relatorio_acessos.csv"'},
        )

    def contar(*extra) -> int:
        return db.scalar(select(func.count()).select_from(Acesso).where(*filtros, *extra)) or 0

    return {
        "periodo_inicio": inicio, "periodo_fim": fim,
        "total": contar(),
        "liberados": contar(Acesso.resultado == ResultadoAcesso.LIBERADO),
        "negados": contar(Acesso.resultado == ResultadoAcesso.NEGADO),
        "aberturas_manuais": contar(Acesso.origem == OrigemAcesso.MANUAL),
        "leituras_automaticas": contar(Acesso.origem == OrigemAcesso.AUTOMATICO),
    }


@router.get("/logs-tecnicos")
def logs_tecnicos(
    linhas: int = Query(200, ge=1, le=2000),
    _: Usuario = Depends(exigir_papeis(PapelUsuario.SUPER_ADMIN)),
):
    """Logs de hardware/software (crash e debug). Exclusivo do Super ADM."""
    arquivo = Path(os.getenv("LOG_DIR", "logs")) / "aegis.log"
    if not arquivo.is_file():
        return {"linhas": []}
    with arquivo.open(encoding="utf-8", errors="replace") as f:
        return {"linhas": [l.rstrip("\n") for l in deque(f, maxlen=linhas)]}
