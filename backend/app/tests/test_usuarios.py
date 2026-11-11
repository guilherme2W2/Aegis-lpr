from app.models import PapelUsuario
from tests import CPFS, SENHA, cabecalho, cliente, criar_usuario, reiniciar_banco


def setup_function():
    reiniciar_banco()


def _novo_usuario(**extra):
    base = {"nome_completo": "Maria da Silva", "email": "maria@exemplo.com", "cpf": "993.518.190-19",
            "unidade": "Apto 12", "telefone": "(11) 98888-7777", "papel": "MORADOR"}
    return {**base, **extra}


def test_login_invalido_e_bloqueio_por_tentativas():
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[0])
    for _ in range(5):
        assert cliente.post("/auth/login", json={"email": "adm@x.com", "senha": "errada"}).status_code == 401
    assert cliente.post("/auth/login", json={"email": "adm@x.com", "senha": SENHA}).status_code == 429


def test_fluxo_primeiro_acesso_exige_troca_de_senha():
    criar_usuario(PapelUsuario.MORADOR, "m@x.com", CPFS[0], primeiro_acesso=True, senha="Temp#1234")
    r = cliente.post("/auth/login", json={"email": "m@x.com", "senha": "Temp#1234"})
    assert r.status_code == 200 and r.json()["primeiro_acesso"] is True
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    assert cliente.get("/auth/me", headers=h).status_code == 403  # token restrito
    assert cliente.get("/veiculos", headers=h).status_code == 403

    fraca = cliente.post("/auth/trocar-senha", headers=h, json={"senha_atual": "Temp#1234", "nova_senha": "abc"})
    assert fraca.status_code == 422
    ok = cliente.post("/auth/trocar-senha", headers=h, json={"senha_atual": "Temp#1234", "nova_senha": "NovaSenha9"})
    assert ok.status_code == 200 and ok.json()["primeiro_acesso"] is False

    # token antigo deixa de valer; o novo funciona
    assert cliente.get("/auth/me", headers=h).status_code == 401
    novo = {"Authorization": f"Bearer {ok.json()['access_token']}"}
    assert cliente.get("/auth/me", headers=novo).status_code == 200


def test_admin_cria_morador_e_cpf_fica_mascarado_para_o_proprio_morador():
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[0])
    h_adm = cabecalho("adm@x.com")
    r = cliente.post("/usuarios", headers=h_adm, json=_novo_usuario())
    assert r.status_code == 201, r.text
    assert r.json()["cpf"] == "99351819019"  # íntegro para Admin
    assert r.json()["primeiro_acesso"] is True and r.json()["email_enviado"] is True

    lista = cliente.get("/usuarios", headers=h_adm).json()
    assert any(u["cpf"] == "99351819019" for u in lista)

    criar_usuario(PapelUsuario.MORADOR, "m@x.com", CPFS[1])
    me = cliente.get("/auth/me", headers=cabecalho("m@x.com")).json()
    assert me["cpf"] == f"***.***.{CPFS[1][6:9]}-**"


def test_validacoes_e_duplicidade():
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[0])
    h = cabecalho("adm@x.com")
    assert cliente.post("/usuarios", headers=h, json=_novo_usuario(cpf="111.111.111-11")).status_code == 422
    assert cliente.post("/usuarios", headers=h, json=_novo_usuario(email="invalido")).status_code == 422
    assert cliente.post("/usuarios", headers=h, json=_novo_usuario()).status_code == 201
    assert cliente.post("/usuarios", headers=h, json=_novo_usuario(cpf="08301661305")).status_code == 409  # e-mail
    assert cliente.post("/usuarios", headers=h, json=_novo_usuario(email="outro@x.com")).status_code == 409  # cpf


def test_permissoes_por_perfil():
    criar_usuario(PapelUsuario.PORTEIRO, "p@x.com", CPFS[0])
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[1])
    criar_usuario(PapelUsuario.SUPER_ADMIN, "sup@x.com", CPFS[2])
    assert cliente.post("/usuarios", headers=cabecalho("p@x.com"), json=_novo_usuario()).status_code == 403
    # Admin não cria outro Admin; Super ADM cria
    assert cliente.post("/usuarios", headers=cabecalho("adm@x.com"), json=_novo_usuario(papel="ADMIN")).status_code == 403
    assert cliente.post("/usuarios", headers=cabecalho("sup@x.com"), json=_novo_usuario(papel="ADMIN")).status_code == 201
    # Admin não enxerga o Super ADM
    nomes = [u["email"] for u in cliente.get("/usuarios", headers=cabecalho("adm@x.com")).json()]
    assert "sup@x.com" not in nomes


def test_sem_token_retorna_401_e_desativacao_bloqueia_login():
    assert cliente.get("/usuarios").status_code == 401
    criar_usuario(PapelUsuario.ADMIN, "adm@x.com", CPFS[0])
    h = cabecalho("adm@x.com")
    mor = cliente.post("/usuarios", headers=h, json=_novo_usuario()).json()
    assert cliente.delete(f"/usuarios/{mor['id']}", headers=h).status_code == 204
    assert cliente.get("/usuarios/moradores", headers=h).json() == []
