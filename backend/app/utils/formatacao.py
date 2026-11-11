"""Funções utilitárias de formatação, máscara e tempo (sem dependências externas)."""
import re
from datetime import datetime, timezone
from typing import Optional


def agora() -> datetime:
    """Horário atual em UTC, sem tzinfo (padrão de armazenamento do banco)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def para_utc_naive(valor: Optional[datetime]) -> Optional[datetime]:
    """Converte um datetime (com ou sem fuso) para UTC sem tzinfo."""
    if valor is None:
        return None
    if valor.tzinfo is not None:
        return valor.astimezone(timezone.utc).replace(tzinfo=None)
    return valor


def somente_digitos(valor: Optional[str]) -> str:
    return re.sub(r"\D", "", valor or "")


def formatar_cpf(cpf: str) -> str:
    d = somente_digitos(cpf)
    if len(d) != 11:
        return cpf
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def mascarar_cpf(cpf: str) -> str:
    """LGPD: ***.***.123-** (exibe apenas os dígitos 7 a 9)."""
    d = somente_digitos(cpf)
    if len(d) != 11:
        return "***.***.***-**"
    return f"***.***.{d[6:9]}-**"


def formatar_placa(placa: str) -> str:
    """Padrão antigo vira ABC-1234; Mercosul permanece ABC1D23."""
    p = (placa or "").upper()
    if re.fullmatch(r"[A-Z]{3}\d{4}", p):
        return f"{p[:3]}-{p[3:]}"
    return p


def formatar_telefone(telefone: str) -> str:
    d = somente_digitos(telefone)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return d


def escapar_csv(valor) -> str:
    """Evita injeção de fórmulas ao abrir o CSV no Excel/LibreOffice."""
    texto = "" if valor is None else str(valor)
    if texto and texto[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + texto
    return texto
