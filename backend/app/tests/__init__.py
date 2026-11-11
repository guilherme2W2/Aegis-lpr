"""Infraestrutura de testes: ambiente isolado (SQLite em memória) e helpers compartilhados."""
import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres-123456"
os.environ["PBKDF2_ITERACOES"] = "1000"
os.environ["SOMENTE_LAN"] = "false"
os.environ["JOB_LIMPEZA_ATIVO"] = "false"
os.environ["EMAIL_MODO"] = "console"
os.environ["RELE_MODO"] = "simulado"
os.environ["CAMERA_API_KEY"] = "camera-teste-123"
os.environ["LOG_DIR"] = tempfile.mkdtemp(prefix="aegis-logs-")

from fastapi.testclient import TestClient  # noqa: E402

from app import database  # noqa: E402
from app.main import app  # noqa: E402
from app.models import PapelUsuario, StatusVeiculo, TipoVeiculo, Usuario, Veiculo  # noqa: E402
from app.security import hash_senha, reiniciar_limitador  # noqa: E402
from app.utils.formatacao import agora  # noqa: E402

cliente = TestClient(app)
SENHA = "Senha@1234"
CAMERA = {"X-Camera-Key": "camera-teste-123"}

CPFS = ["52601815906", "08301661305", "18609139034", "99603082430", "62819482112", "99351819019"]


def reiniciar_banco() -> None:
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    reiniciar_limitador()


def criar_usuario(papel: PapelUsuario, email: str, cpf: str, nome: str = "Fulano de Tal",
                  unidade: str = "101", primeiro_acesso: bool = False, senha: str = SENHA) -> Usuario:
    with database.SessionLocal() as db:
        u = Usuario(nome_completo=nome, email=email, cpf=cpf, unidade=unidade, telefone="11999998888",
                    papel=papel, senha_hash=hash_senha(senha), primeiro_acesso=primeiro_acesso, ativo=True)
        db.add(u)
        db.commit()
        db.refresh(u)
        return u


def cabecalho(email: str, senha: str = SENHA) -> dict:
    resp = cliente.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def criar_veiculo_direto(placa: str, dono_id: int, tipo=TipoVeiculo.MORADOR, status=StatusVeiculo.ATIVO,
                         expira_em=None, desativado_em=None, duracao_horas=None) -> Veiculo:
    with database.SessionLocal() as db:
        v = Veiculo(placa=placa, modelo="Gol", cor="Prata", tipo=tipo, status=status, dono_id=dono_id,
                    expira_em=expira_em, desativado_em=desativado_em, duracao_horas=duracao_horas)
        db.add(v)
        db.commit()
        db.refresh(v)
        return v
