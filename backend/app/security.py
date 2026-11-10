"""Segurança: hash de senha, JWT (HS256), RBAC, chave da câmera e restrição à rede local.

JWT e hash de senha usam apenas a biblioteca padrão (hmac/hashlib), sem dependências extras.
"""
import base64
import hashlib
import hmac
import ipaddress
import json
import logging
import os
import secrets
import time
from typing import Callable, Optional

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import PapelUsuario, Usuario

load_dotenv()
logger = logging.getLogger("aegis.security")


# --------------------------------------------------------------------------- senha
def _iteracoes() -> int:
    return int(os.getenv("PBKDF2_ITERACOES", "310000"))


def _b64e(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode()


def _b64d(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    iteracoes = _iteracoes()
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, iteracoes)
    return f"pbkdf2_sha256${iteracoes}${_b64e(sal)}${_b64e(h)}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        algoritmo, iteracoes, sal, esperado = armazenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        h = hashlib.pbkdf2_hmac("sha256", senha.encode(), _b64d(sal), int(iteracoes))
        return hmac.compare_digest(h, _b64d(esperado))
    except Exception:
        return False


def gerar_senha_temporaria(tamanho: int = 12) -> str:
    maiusculas = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    minusculas = "abcdefghijkmnopqrstuvwxyz"
    numeros = "23456789"
    simbolos = "@#%&*"
    todos = maiusculas + minusculas + numeros + simbolos
    while True:
        senha = "".join(secrets.choice(todos) for _ in range(tamanho))
        if (any(c in maiusculas for c in senha) and any(c in minusculas for c in senha)
                and any(c in numeros for c in senha)):
            return senha


# --------------------------------------------------------------------------- JWT
class TokenInvalido(Exception):
    pass


def _segredo() -> bytes:
    segredo = os.getenv("JWT_SECRET_KEY", "")
    if len(segredo) < 32:
        raise RuntimeError("JWT_SECRET_KEY ausente ou curta demais (mínimo 32 caracteres). Veja o .env.example.")
    return segredo.encode()


def _assinar(conteudo: str) -> str:
    return _b64e(hmac.new(_segredo(), conteudo.encode(), hashlib.sha256).digest())


def criar_token(payload: dict, minutos: int) -> str:
    agora = int(time.time())
    cabecalho = _b64e(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    corpo = _b64e(json.dumps({**payload, "iat": agora, "exp": agora + minutos * 60}, separators=(",", ":")).encode())
    conteudo = f"{cabecalho}.{corpo}"
    return f"{conteudo}.{_assinar(conteudo)}"


def decodificar_token(token: str) -> dict:
    try:
        cabecalho_b64, corpo_b64, assinatura = token.split(".")
        cabecalho = json.loads(_b64d(cabecalho_b64))
        if cabecalho.get("alg") != "HS256":
            raise TokenInvalido("Algoritmo não suportado")
        if not hmac.compare_digest(_assinar(f"{cabecalho_b64}.{corpo_b64}"), assinatura):
            raise TokenInvalido("Assinatura inválida")
        dados = json.loads(_b64d(corpo_b64))
    except TokenInvalido:
        raise
    except Exception as exc:
        raise TokenInvalido("Token malformado") from exc
    if int(dados.get("exp", 0)) < int(time.time()):
        raise TokenInvalido("Token expirado")
    return dados


def _impressao_senha(usuario: Usuario) -> str:
    """Muda quando a senha muda => tokens antigos deixam de valer."""
    return hashlib.sha256(usuario.senha_hash.encode()).hexdigest()[:16]


def criar_token_para_usuario(usuario: Usuario) -> tuple[str, int]:
    """Token de primeiro acesso (curto e restrito) ou token normal."""
    if usuario.primeiro_acesso:
        minutos = int(os.getenv("TOKEN_PRIMEIRO_ACESSO_MINUTOS", "15"))
        tipo = "primeiro_acesso"
    else:
        minutos = int(os.getenv("TOKEN_EXPIRA_MINUTOS", "60"))
        tipo = "acesso"
    token = criar_token(
        {"sub": str(usuario.id), "papel": usuario.papel.value, "tipo": tipo, "ph": _impressao_senha(usuario)},
        minutos,
    )
    return token, minutos


# --------------------------------------------------------------------------- limitador de login
_falhas: dict[str, list[float]] = {}


def _janela() -> int:
    return int(os.getenv("LOGIN_JANELA_SEGUNDOS", "300"))


def _max_falhas() -> int:
    return int(os.getenv("LOGIN_MAX_FALHAS", "5"))


def _podar(chave: str) -> list[float]:
    limite = time.time() - _janela()
    recentes = [t for t in _falhas.get(chave, []) if t > limite]
    _falhas[chave] = recentes
    return recentes


def verificar_bloqueio(chave: str) -> None:
    if len(_podar(chave)) >= _max_falhas():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Aguarde alguns minutos.",
            headers={"Retry-After": str(_janela())},
        )


def registrar_falha(chave: str) -> None:
    _podar(chave).append(time.time())


def limpar_falhas(chave: str) -> None:
    _falhas.pop(chave, None)


def reiniciar_limitador() -> None:
    _falhas.clear()


# --------------------------------------------------------------------------- dependências (RBAC)
_bearer = HTTPBearer(auto_error=False)


def _obter_usuario(credenciais: Optional[HTTPAuthorizationCredentials], db: Session, permitir_primeiro_acesso: bool) -> Usuario:
    nao_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciais is None:
        raise nao_autenticado
    try:
        dados = decodificar_token(credenciais.credentials)
        usuario = db.get(Usuario, int(dados["sub"]))
    except (TokenInvalido, KeyError, ValueError):
        raise nao_autenticado
    if usuario is None or not usuario.ativo or dados.get("ph") != _impressao_senha(usuario):
        raise nao_autenticado
    if (dados.get("tipo") == "primeiro_acesso" or usuario.primeiro_acesso) and not permitir_primeiro_acesso:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Troca de senha obrigatória no primeiro acesso")
    return usuario


def usuario_atual(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(_bearer), db: Session = Depends(get_db)
) -> Usuario:
    return _obter_usuario(credenciais, db, permitir_primeiro_acesso=False)


def usuario_primeiro_acesso(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(_bearer), db: Session = Depends(get_db)
) -> Usuario:
    return _obter_usuario(credenciais, db, permitir_primeiro_acesso=True)


def exigir_papeis(*papeis: PapelUsuario) -> Callable[..., Usuario]:
    def dependencia(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.papel not in papeis:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão para esta operação")
        return usuario

    return dependencia


def validar_chave_camera(x_camera_key: str = Header(default="")) -> None:
    """Autentica a câmera/listener LPR (dispositivo, não é um usuário JWT)."""
    esperada = os.getenv("CAMERA_API_KEY", "")
    if not esperada or not hmac.compare_digest(x_camera_key.encode(), esperada.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chave da câmera inválida")


# --------------------------------------------------------------------------- rede local
def _redes_extras() -> list:
    redes = []
    for item in os.getenv("REDES_PERMITIDAS", "").split(","):
        item = item.strip()
        if item:
            try:
                redes.append(ipaddress.ip_network(item, strict=False))
            except ValueError:
                logger.warning("REDES_PERMITIDAS contém valor inválido: %s", item)
    return redes


def ip_permitido(host: str) -> bool:
    """True para loopback, redes privadas (RFC1918), link-local e redes extras do .env."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    if getattr(ip, "ipv4_mapped", None):
        ip = ip.ipv4_mapped
    if ip.is_loopback or ip.is_private or ip.is_link_local:
        return True
    return any(ip in rede for rede in _redes_extras())
