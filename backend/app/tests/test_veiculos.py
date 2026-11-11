from datetime import timedelta

from app import database
from app.models import PapelUsuario, StatusVeiculo, TipoVeiculo, Veiculo
from app.utils.formatacao import agora
from tests import CPFS, cabecalho, cliente, criar_usuario, criar_veiculo_direto, reiniciar_banco


def setup_function():
    reiniciar_banco()
    global adm, por, mor1, mor2
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[0], nome="Admin Um")
    por = criar_usuario(PapelUsuario.PORTEIRO, "p@x.com", CPFS[1], nome="Porteiro Um")
    mor1 = criar_usuario(PapelUsuario.MORADOR, "m1@x.com", CPFS[2], nome="Morador Um", unidade="101")
    mor2 = criar_usuario(PapelUsuario.MORADOR, "m2@x.com", CPFS[3], nome="Morador Dois", unidade="102")


def _visitante(placa, morador_id, horas=2):
    return cliente.post("/veiculos/visitantes", headers=cabecalho("p@x.com"),
                        json={"placa": placa, "modelo": "Uno", "cor": "Azul", "morador_id": morador_id, "duracao_horas": horas})


def test_admin_cadastra_carro_fixo_e_porteiro_nao():
    corpo = {"placa": "abc-1d23", "modelo": "Onix", "cor": "Preto", "dono_id": mor1.id}
    assert cliente.post("/veiculos/moradores", headers=cabecalho("p@x.com"), json=corpo).status_code == 403
    r = cliente.post("/veiculos/moradores", headers=cabecalho("adm@x.com"), json=corpo)
    assert r.status_code == 201, r.text
    assert r.json()["placa"] == "ABC1D23" and r.json()["tipo"] == "MORADOR" and r.json()["dono_unidade"] == "101"
    assert cliente.post("/veiculos/moradores", headers=cabecalho("adm@x.com"), json=corpo).status_code == 409


def test_placa_invalida_retorna_422():
    corpo = {"placa": "12345", "modelo": "Onix", "cor": "Preto", "dono_id": mor1.id}
    assert cliente.post("/veiculos/moradores", headers=cabecalho("adm@x.com"), json=corpo).status_code == 422


def test_visitante_com_duracao_e_limite_de_dois_por_morador():
    r = _visitante("AAA1111", mor1.id, horas=12)
    assert r.status_code == 201 and r.json()["status"] == "ATIVO" and r.json()["duracao_horas"] == 12
    assert _visitante("BBB2222", mor1.id).status_code == 201
    assert _visitante("CCC3333", mor1.id).status_code == 409
    assert _visitante("CCC3333", mor2.id).status_code == 201  # outro morador não é afetado


def test_escopo_de_listagem_por_perfil():
    criar_veiculo_direto("FIX1A11", mor1.id)
    criar_veiculo_direto("FIX2B22", mor2.id)
    _visitante("VIS1111", mor1.id)
    assert len(cliente.get("/veiculos", headers=cabecalho("adm@x.com")).json()) == 3
    assert {v["placa"] for v in cliente.get("/veiculos", headers=cabecalho("m1@x.com")).json()} == {"FIX1A11", "VIS1111"}
    assert {v["placa"] for v in cliente.get("/veiculos", headers=cabecalho("p@x.com")).json()} == {"VIS1111"}


def test_morador_nao_acessa_veiculo_de_outro():
    outro = criar_veiculo_direto("FIX2B22", mor2.id)
    assert cliente.get(f"/veiculos/{outro.id}", headers=cabecalho("m1@x.com")).status_code == 404


def test_saida_desativa_e_reativacao_dentro_de_48h():
    vid = _visitante("VIS1111", mor1.id).json()["id"]
    h = cabecalho("p@x.com")
    r = cliente.post(f"/veiculos/{vid}/saida", headers=h)
    assert r.json()["status"] == "DESATIVADO" and r.json()["desativado_em"]
    r = cliente.post(f"/veiculos/{vid}/reativar", headers=h, json={"duracao_horas": 3})
    assert r.status_code == 200 and r.json()["status"] == "ATIVO" and r.json()["duracao_horas"] == 3


def test_reativacao_apos_48h_e_negada():
    v = criar_veiculo_direto("VIS9999", mor1.id, tipo=TipoVeiculo.VISITANTE, status=StatusVeiculo.DESATIVADO,
                             desativado_em=agora() - timedelta(hours=49), duracao_horas=2)
    r = cliente.post(f"/veiculos/{v.id}/reativar", headers=cabecalho("p@x.com"))
    assert r.status_code == 409 and "48h" in r.json()["detail"]


def test_remover_carro_fixo_preserva_historico():
    v = criar_veiculo_direto("FIX1A11", mor1.id)
    r = cliente.post("/acessos/lpr/placa", headers={"X-Camera-Key": "camera-teste-123"}, json={"placa": "FIX1A11"})
    assert r.json()["liberado"] is True
    assert cliente.delete(f"/veiculos/{v.id}", headers=cabecalho("adm@x.com")).status_code == 204
    hist = cliente.get("/acessos", headers=cabecalho("adm@x.com")).json()
    assert len(hist) == 1 and hist[0]["veiculo_id"] is None and hist[0]["placa"] == "FIX1A11"
