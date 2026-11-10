from datetime import timedelta

from app import database
from app.models import PapelUsuario, StatusVeiculo, TipoVeiculo, Veiculo
from app.services import controle_acesso, reconhecimento
from app.utils.formatacao import agora
from tests import CAMERA, CPFS, cabecalho, cliente, criar_usuario, criar_veiculo_direto, reiniciar_banco


class ReleFalso:
    def __init__(self, ok=True):
        self.chamadas = 0
        self.ok = ok

    def acionar(self):
        self.chamadas += 1
        return self.ok


def setup_function():
    reiniciar_banco()
    global mor1, mor2
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[0])
    criar_usuario(PapelUsuario.PORTEIRO, "p@x.com", CPFS[1], nome="Carlos Porteiro")
    criar_usuario(PapelUsuario.SUPER_ADMIN, "sup@x.com", CPFS[4])
    mor1 = criar_usuario(PapelUsuario.MORADOR, "m1@x.com", CPFS[2], nome="Morador Um")
    mor2 = criar_usuario(PapelUsuario.MORADOR, "m2@x.com", CPFS[3], nome="Morador Dois")


def _ler(placa):
    return cliente.post("/acessos/lpr/placa", headers=CAMERA, json={"placa": placa})


def test_camera_exige_chave():
    assert cliente.post("/acessos/lpr/placa", json={"placa": "ABC1D23"}).status_code == 401
    assert cliente.post("/acessos/lpr/placa", headers={"X-Camera-Key": "errada"}, json={"placa": "ABC1D23"}).status_code == 401


def test_placa_autorizada_aciona_rele(monkeypatch):
    rele = ReleFalso()
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: rele)
    criar_veiculo_direto("ABC1D23", mor1.id)
    r = _ler("abc-1d23").json()
    assert r["liberado"] is True and r["rele_acionado"] is True and rele.chamadas == 1


def test_falhas_de_validacao_geram_log_e_mantem_portao_fechado(monkeypatch):
    rele = ReleFalso()
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: rele)
    criar_veiculo_direto("OFF1A11", mor1.id, status=StatusVeiculo.DESATIVADO)
    assert _ler("XYZ9K99").json()["motivo"] == "Placa não cadastrada"
    assert _ler("OFF1A11").json()["motivo"] == "Placa desativada"
    assert _ler("@@").json()["motivo"].startswith("Placa ilegível")
    assert rele.chamadas == 0
    hist = cliente.get("/acessos", headers=cabecalho("adm@x.com")).json()
    assert len(hist) == 3 and all(a["resultado"] == "NEGADO" and not a["rele_acionado"] for a in hist)


def test_visitante_expirado_e_negado_e_desativado(monkeypatch):
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: ReleFalso())
    v = criar_veiculo_direto("VIS1A11", mor1.id, tipo=TipoVeiculo.VISITANTE, expira_em=agora() - timedelta(minutes=1), duracao_horas=1)
    assert _ler("VIS1A11").json()["liberado"] is False
    with database.SessionLocal() as db:
        assert db.get(Veiculo, v.id).status == StatusVeiculo.DESATIVADO


def test_falha_do_rele_nega_acesso(monkeypatch):
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: ReleFalso(ok=False))
    criar_veiculo_direto("ABC1D23", mor1.id)
    r = _ler("ABC1D23").json()
    assert r["liberado"] is False and "relé" in r["motivo"]


def test_abertura_manual_registra_nome_do_porteiro(monkeypatch):
    rele = ReleFalso()
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: rele)
    assert cliente.post("/acessos/abertura-manual", headers=cabecalho("m1@x.com"), json={"motivo": "placa suja"}).status_code == 403
    r = cliente.post("/acessos/abertura-manual", headers=cabecalho("p@x.com"), json={"motivo": "placa suja"})
    assert r.status_code == 200 and r.json()["liberado"] is True and rele.chamadas == 1
    hist = cliente.get("/acessos", headers=cabecalho("adm@x.com")).json()
    assert hist[0]["origem"] == "MANUAL" and "Abertura Manual por Carlos Porteiro" in hist[0]["motivo"]
    assert hist[0]["operador_nome"] == "Carlos Porteiro"


def test_morador_ve_somente_o_proprio_historico(monkeypatch):
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: ReleFalso())
    criar_veiculo_direto("AAA1A11", mor1.id)
    criar_veiculo_direto("BBB2B22", mor2.id)
    _ler("AAA1A11")
    _ler("BBB2B22")
    meu = cliente.get("/acessos", headers=cabecalho("m1@x.com")).json()
    assert [a["placa"] for a in meu] == ["AAA1A11"]
    assert len(cliente.get("/acessos", headers=cabecalho("p@x.com")).json()) == 2


def test_relatorio_e_logs_tecnicos_por_perfil(monkeypatch):
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: ReleFalso())
    criar_veiculo_direto("AAA1A11", mor1.id)
    _ler("AAA1A11")
    _ler("ZZZ9Z99")
    rel = cliente.get("/acessos/relatorio", headers=cabecalho("adm@x.com")).json()
    assert rel["total"] == 2 and rel["liberados"] == 1 and rel["negados"] == 1
    csv = cliente.get("/acessos/relatorio?formato=csv", headers=cabecalho("adm@x.com"))
    assert csv.headers["content-type"].startswith("text/csv") and "AAA1A11" in csv.text
    assert cliente.get("/acessos/relatorio", headers=cabecalho("p@x.com")).status_code == 403
    assert cliente.get("/acessos/logs-tecnicos", headers=cabecalho("adm@x.com")).status_code == 403
    assert cliente.get("/acessos/logs-tecnicos", headers=cabecalho("sup@x.com")).status_code == 200


def test_job_remove_visitantes_desativados_ha_mais_de_48h():
    antigo = criar_veiculo_direto("OLD1A11", mor1.id, tipo=TipoVeiculo.VISITANTE, status=StatusVeiculo.DESATIVADO,
                                  desativado_em=agora() - timedelta(hours=49))
    recente = criar_veiculo_direto("NEW1A11", mor1.id, tipo=TipoVeiculo.VISITANTE, status=StatusVeiculo.DESATIVADO,
                                   desativado_em=agora() - timedelta(hours=10))
    vencido = criar_veiculo_direto("EXP1A11", mor1.id, tipo=TipoVeiculo.VISITANTE, expira_em=agora() - timedelta(hours=1))
    fixo = criar_veiculo_direto("FIX1A11", mor1.id, status=StatusVeiculo.DESATIVADO, desativado_em=agora() - timedelta(days=90))
    assert controle_acesso.executar_limpeza() == {"desativados": 1, "removidos": 1}
    with database.SessionLocal() as db:
        assert db.get(Veiculo, antigo.id) is None
        assert db.get(Veiculo, recente.id) is not None
        assert db.get(Veiculo, vencido.id).status == StatusVeiculo.DESATIVADO
        assert db.get(Veiculo, fixo.id) is not None  # carros fixos nunca são apagados pelo job


def test_endpoint_de_imagem_usa_o_reconhecedor(monkeypatch):
    monkeypatch.setattr(controle_acesso, "obter_rele", lambda: ReleFalso())
    criar_veiculo_direto("ABC1D23", mor1.id)

    class Falso:
        def reconhecer(self, dados):
            if dados == b"corrompida":
                raise reconhecimento.ErroImagem("imagem inválida")
            return reconhecimento.LeituraPlaca("ABC1D23", 0.91)

    monkeypatch.setattr(reconhecimento, "obter_reconhecedor", lambda: Falso())
    r = cliente.post("/acessos/lpr/imagem", headers=CAMERA, content=b"\xff\xd8fake")
    assert r.status_code == 200 and r.json()["liberado"] is True and r.json()["confianca"] == 0.91
    assert cliente.post("/acessos/lpr/imagem", headers=CAMERA, content=b"corrompida").status_code == 400
    assert cliente.post("/acessos/lpr/imagem", content=b"x").status_code == 401
