"""Regras de acesso: decide se o portão abre, aciona o relé, registra o log e limpa visitantes.

Isolamento: a API nunca fala com o hardware diretamente; apenas chama este módulo, e o
módulo só envia um PULSO ao microcontrolador (nunca "abrir e manter"), de modo que o
próprio hardware fecha o portão mesmo que o servidor caia (ver docs/controle_acesso.md).
"""
import asyncio
import json
import logging
import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app import database
from app.models.acesso import Acesso, OrigemAcesso, ResultadoAcesso
from app.models.usuario import Usuario
from app.models.veiculo import StatusVeiculo, TipoVeiculo, Veiculo
from app.services.validacao import normalizar_placa, placa_valida
from app.utils.formatacao import agora

logger = logging.getLogger("aegis.acesso")

JANELA_REATIVACAO = timedelta(hours=48)


def max_visitantes_por_morador() -> int:
    return int(os.getenv("MAX_VISITANTES_POR_MORADOR", "2"))


# ============================================================================ relé
class RelePortao:
    """Driver do relé. Modos: 'simulado' (apenas loga) ou 'http' (microcontrolador na LAN)."""

    def __init__(self) -> None:
        self.modo = os.getenv("RELE_MODO", "simulado").lower()
        self.url = os.getenv("RELE_URL", "")
        self.token = os.getenv("RELE_TOKEN", "")
        self.pulso_ms = int(os.getenv("RELE_PULSO_MS", "3000"))
        self.timeout_s = float(os.getenv("RELE_TIMEOUT_S", "2"))

    def acionar(self) -> bool:
        if self.modo == "simulado":
            logger.info("[RELÉ SIMULADO] pulso de %d ms", self.pulso_ms)
            return True
        if self.modo == "http":
            try:
                corpo = json.dumps({"acao": "pulso", "duracao_ms": self.pulso_ms}).encode()
                req = urllib.request.Request(
                    self.url, data=corpo, method="POST",
                    headers={"Content-Type": "application/json", "X-Rele-Token": self.token},
                )
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    return 200 <= resp.status < 300
            except Exception:
                logger.exception("Falha ao acionar o relé em %s", self.url)
                return False
        logger.error("RELE_MODO inválido: %s", self.modo)
        return False


_rele: Optional[RelePortao] = None


def obter_rele() -> RelePortao:
    global _rele
    if _rele is None:
        _rele = RelePortao()
    return _rele


# ============================================================================ decisão
@dataclass
class Decisao:
    acesso_id: int
    placa: str
    liberado: bool
    motivo: str
    rele_acionado: bool
    confianca: Optional[float] = None


def desativar_veiculo(veiculo: Veiculo, quando: Optional[datetime] = None) -> None:
    veiculo.status = StatusVeiculo.DESATIVADO
    veiculo.desativado_em = quando or agora()


def avaliar_veiculo(db: Session, placa: str, momento: Optional[datetime] = None) -> tuple[bool, str, Optional[Veiculo]]:
    momento = momento or agora()
    veiculo = db.scalar(select(Veiculo).where(Veiculo.placa == placa))
    if veiculo is None:
        return False, "Placa não cadastrada", None
    if veiculo.status != StatusVeiculo.ATIVO:
        return False, "Placa desativada", veiculo
    if veiculo.tipo == TipoVeiculo.VISITANTE and veiculo.expira_em and veiculo.expira_em <= momento:
        desativar_veiculo(veiculo, quando=veiculo.expira_em)
        db.commit()
        return False, "Permanência do visitante expirada", veiculo
    if veiculo.dono is None or not veiculo.dono.ativo:
        return False, "Morador responsável inativo", veiculo
    return True, "Placa autorizada", veiculo


def registrar_acesso(
    db: Session, placa: str, resultado: ResultadoAcesso, origem: OrigemAcesso, motivo: str,
    veiculo: Optional[Veiculo] = None, operador: Optional[Usuario] = None,
    confianca: Optional[float] = None, rele_acionado: bool = False,
) -> Acesso:
    acesso = Acesso(
        placa=placa[:10], veiculo_id=veiculo.id if veiculo else None,
        morador_id=veiculo.dono_id if veiculo else None,
        operador_id=operador.id if operador else None,
        resultado=resultado, origem=origem, motivo=motivo[:255],
        confianca=confianca, rele_acionado=rele_acionado,
    )
    db.add(acesso)
    db.commit()
    db.refresh(acesso)
    logger.info("ACESSO %s | placa=%s | origem=%s | %s", resultado.value, acesso.placa, origem.value, acesso.motivo)
    return acesso


def processar_leitura(db: Session, placa_lida: Optional[str], confianca: Optional[float] = None) -> Decisao:
    """Câmera captura placa -> valida cadastro/status ATIVO -> aciona relé -> registra log.
    Qualquer falha gera log e mantém o portão fechado."""
    placa = normalizar_placa(placa_lida)
    if not placa_valida(placa):
        acesso = registrar_acesso(
            db, placa or "ILEGIVEL", ResultadoAcesso.NEGADO, OrigemAcesso.AUTOMATICO,
            "Placa ilegível ou formato inválido", confianca=confianca,
        )
        return Decisao(acesso.id, acesso.placa, False, acesso.motivo, False, confianca)

    liberado, motivo, veiculo = avaliar_veiculo(db, placa)
    rele_ok = False
    if liberado:
        rele_ok = obter_rele().acionar()
        if not rele_ok:
            liberado, motivo = False, "Autorizado, mas houve falha no acionamento do relé"
            logger.critical("Falha no relé ao liberar a placa %s", placa)

    acesso = registrar_acesso(
        db, placa, ResultadoAcesso.LIBERADO if liberado else ResultadoAcesso.NEGADO,
        OrigemAcesso.AUTOMATICO, motivo, veiculo=veiculo, confianca=confianca, rele_acionado=rele_ok,
    )
    return Decisao(acesso.id, placa, liberado, motivo, rele_ok, confianca)


def abertura_manual(db: Session, operador: Usuario, motivo: str, placa_informada: Optional[str] = None) -> Decisao:
    """Gatilho manual do porteiro (placa suja/ilegível). Sempre auditado com o nome do operador."""
    placa = normalizar_placa(placa_informada)
    veiculo = db.scalar(select(Veiculo).where(Veiculo.placa == placa)) if placa_valida(placa) else None
    rele_ok = obter_rele().acionar()
    texto = f"Abertura Manual por {operador.nome_completo}: {motivo}"
    if not rele_ok:
        texto = "Falha no acionamento do relé. " + texto
    acesso = registrar_acesso(
        db, placa or "MANUAL", ResultadoAcesso.LIBERADO if rele_ok else ResultadoAcesso.NEGADO,
        OrigemAcesso.MANUAL, texto, veiculo=veiculo, operador=operador, rele_acionado=rele_ok,
    )
    return Decisao(acesso.id, acesso.placa, rele_ok, texto, rele_ok)


# ============================================================================ visitantes
def contar_visitantes_ativos(db: Session, morador_id: int, ignorar_id: Optional[int] = None) -> int:
    consulta = select(func.count()).select_from(Veiculo).where(
        Veiculo.dono_id == morador_id, Veiculo.tipo == TipoVeiculo.VISITANTE, Veiculo.status == StatusVeiculo.ATIVO,
    )
    if ignorar_id is not None:
        consulta = consulta.where(Veiculo.id != ignorar_id)
    return db.scalar(consulta) or 0


def reativar_visitante(db: Session, veiculo: Veiculo, duracao_horas: Optional[int] = None) -> Veiculo:
    """Porteiro pode reativar placa temporária desativada há no máximo 48h."""
    momento = agora()
    if veiculo.tipo != TipoVeiculo.VISITANTE:
        raise ValueError("Apenas veículos de visitantes podem ser reativados")
    if veiculo.status != StatusVeiculo.DESATIVADO:
        raise ValueError("O veículo já está ativo")
    if veiculo.desativado_em is None or momento - veiculo.desativado_em > JANELA_REATIVACAO:
        raise ValueError("Prazo de 48h para reativação expirado; cadastre o visitante novamente")
    if contar_visitantes_ativos(db, veiculo.dono_id, ignorar_id=veiculo.id) >= max_visitantes_por_morador():
        raise ValueError(f"O morador já possui {max_visitantes_por_morador()} visitantes ativos")
    horas = duracao_horas or veiculo.duracao_horas or 1
    veiculo.status = StatusVeiculo.ATIVO
    veiculo.desativado_em = None
    veiculo.duracao_horas = horas
    veiculo.expira_em = momento + timedelta(hours=horas)
    db.commit()
    db.refresh(veiculo)
    return veiculo


def desativar_expirados(db: Session, momento: Optional[datetime] = None) -> int:
    """Visitantes ATIVOS cujo prazo acabou passam a DESATIVADO."""
    momento = momento or agora()
    expirados = db.scalars(select(Veiculo).where(
        Veiculo.tipo == TipoVeiculo.VISITANTE, Veiculo.status == StatusVeiculo.ATIVO,
        Veiculo.expira_em.is_not(None), Veiculo.expira_em <= momento,
    )).all()
    for v in expirados:
        desativar_veiculo(v, quando=v.expira_em)
    if expirados:
        db.commit()
    return len(expirados)


def remover_veiculo(db: Session, veiculo: Veiculo) -> None:
    """Apaga o veículo preservando o histórico (os logs mantêm a placa; veiculo_id vira NULL)."""
    db.execute(update(Acesso).where(Acesso.veiculo_id == veiculo.id).values(veiculo_id=None))
    db.delete(veiculo)


def limpar_visitantes_expirados(db: Session, momento: Optional[datetime] = None) -> dict:
    """Job diário: desativa visitantes vencidos e DELETA placas desativadas há mais de 48h."""
    momento = momento or agora()
    desativados = desativar_expirados(db, momento)
    antigos = db.scalars(select(Veiculo).where(
        Veiculo.tipo == TipoVeiculo.VISITANTE, Veiculo.status == StatusVeiculo.DESATIVADO,
        Veiculo.desativado_em.is_not(None), Veiculo.desativado_em < momento - JANELA_REATIVACAO,
    )).all()
    for v in antigos:
        remover_veiculo(db, v)
    db.commit()
    resumo = {"desativados": desativados, "removidos": len(antigos)}
    logger.info("Job de limpeza de visitantes: %s", resumo)
    return resumo


def executar_limpeza() -> dict:
    with database.SessionLocal() as db:
        return limpar_visitantes_expirados(db)


def _segundos_ate(horario: str) -> float:
    hora, minuto = (int(p) for p in horario.split(":"))
    agora_local = datetime.now()
    alvo = agora_local.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    if alvo <= agora_local:
        alvo += timedelta(days=1)
    return (alvo - agora_local).total_seconds()


async def loop_limpeza_diaria() -> None:
    """Agendador diário embutido (horário do servidor em JOB_LIMPEZA_HORARIO, padrão 03:00)."""
    horario = os.getenv("JOB_LIMPEZA_HORARIO", "03:00")
    while True:
        try:
            await asyncio.to_thread(executar_limpeza)  # também roda na subida do sistema
        except Exception:
            logger.exception("Erro no job de limpeza")
        await asyncio.sleep(_segundos_ate(horario))
