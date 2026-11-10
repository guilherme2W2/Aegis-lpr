"""AEGIS-LPR - API de automação de portão por leitura de placa (100% rede local)."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

load_dotenv()

from app import database  # noqa: E402
from app.models import PapelUsuario, Usuario  # noqa: E402  (registra os models no metadata)
from app.routers import acessos, autenticacao, usuarios, veiculos  # noqa: E402
from app.security import hash_senha, ip_permitido  # noqa: E402
from app.services import controle_acesso, validacao  # noqa: E402

logger = logging.getLogger("aegis")


def configurar_logs() -> None:
    """Log técnico em arquivo (consultável apenas pelo Super ADM em /acessos/logs-tecnicos)."""
    raiz = logging.getLogger("aegis")
    if raiz.handlers:
        return
    raiz.setLevel(os.getenv("LOG_NIVEL", "INFO").upper())
    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formato)
    raiz.addHandler(console)
    pasta = Path(os.getenv("LOG_DIR", "logs"))
    try:
        pasta.mkdir(parents=True, exist_ok=True)
        arquivo = RotatingFileHandler(pasta / "aegis.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        arquivo.setFormatter(formato)
        raiz.addHandler(arquivo)
    except OSError:
        logger.warning("Não foi possível criar o arquivo de log em %s", pasta)


def garantir_super_admin() -> None:
    """Cria o Super ADM inicial a partir do .env (senha temporária: troca obrigatória no 1º login)."""
    with database.SessionLocal() as db:
        if db.scalar(select(Usuario).where(Usuario.papel == PapelUsuario.SUPER_ADMIN)):
            return
        try:
            email = validacao.validar_email(os.getenv("SUPER_ADMIN_EMAIL", ""))
            cpf = validacao.validar_cpf(os.getenv("SUPER_ADMIN_CPF", ""))
            senha = os.environ["SUPER_ADMIN_SENHA_INICIAL"]
        except (ValueError, KeyError):
            logger.error("Super ADM não criado: defina SUPER_ADMIN_EMAIL, SUPER_ADMIN_CPF e SUPER_ADMIN_SENHA_INICIAL no .env")
            return
        db.add(Usuario(
            nome_completo=os.getenv("SUPER_ADMIN_NOME", "Super Administrador"), email=email, cpf=cpf,
            unidade=os.getenv("SUPER_ADMIN_UNIDADE", "ADM"),
            telefone=validacao.validar_telefone(os.getenv("SUPER_ADMIN_TELEFONE", "11999999999")),
            papel=PapelUsuario.SUPER_ADMIN, senha_hash=hash_senha(senha), primeiro_acesso=True, ativo=True,
        ))
        db.commit()
        logger.info("Super ADM inicial criado (%s). Troque a senha no primeiro login.", email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configurar_logs()
    database.Base.metadata.create_all(bind=database.engine)
    garantir_super_admin()
    tarefa = None
    if os.getenv("JOB_LIMPEZA_ATIVO", "true").lower() == "true":
        tarefa = asyncio.create_task(controle_acesso.loop_limpeza_diaria())
    logger.info("AEGIS-LPR iniciado (somente LAN: %s)", os.getenv("SOMENTE_LAN", "true"))
    yield
    if tarefa:
        tarefa.cancel()


app = FastAPI(
    title="AEGIS-LPR",
    description="Controle de acesso veicular por leitura de placa (LPR) - rede local.",
    version="1.0.0",
    lifespan=lifespan,
)

origens = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if origens:
    app.add_middleware(
        CORSMiddleware, allow_origins=origens, allow_methods=["*"], allow_headers=["*"], allow_credentials=False,
    )


@app.middleware("http")
async def somente_rede_local(request: Request, call_next):
    """Blindagem 100% LAN: recusa qualquer cliente fora de loopback/redes privadas."""
    if os.getenv("SOMENTE_LAN", "true").lower() == "true":
        host = request.client.host if request.client else ""
        if not ip_permitido(host):
            logger.warning("Acesso bloqueado de origem externa: %s", host)
            return JSONResponse(status_code=403, content={"detail": "Acesso permitido apenas pela rede local"})
    return await call_next(request)


app.include_router(autenticacao.router)
app.include_router(usuarios.router)
app.include_router(veiculos.router)
app.include_router(acessos.router)


@app.get("/saude", tags=["Sistema"])
def saude():
    return {"status": "ok"}
