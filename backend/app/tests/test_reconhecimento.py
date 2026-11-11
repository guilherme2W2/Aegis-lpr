import numpy as np
import pytest

from app.services.reconhecimento import ErroImagem, ReconhecedorPlaca, extrair_placa
from app.services.validacao import corrigir_placa, placa_valida, validar_cpf
from app.utils.formatacao import formatar_placa, mascarar_cpf


def test_placa_valida_antiga_e_mercosul():
    assert placa_valida("ABC1234") and placa_valida("ABC1D23")
    assert not placa_valida("AB12345") and not placa_valida("ABCD123")


def test_corrige_confusao_letra_numero_por_posicao():
    assert corrigir_placa("A8C-1234") == "ABC1234"   # 8 -> B nas 3 primeiras posições
    assert corrigir_placa("ABCI23S") == "ABC1235"    # I -> 1 e S -> 5 nas posições numéricas
    assert corrigir_placa("ABC1D2") is None


def test_extrair_placa_de_fragmentos():
    assert extrair_placa([("BRASIL", 0.9), ("ABC1D23", 0.8)]) == ("ABC1D23", 0.8)
    placa, conf = extrair_placa([("BRASIL", 0.9), ("ABC", 0.7), ("1D23", 0.5)])
    assert placa == "ABC1D23" and conf == pytest.approx(0.7)
    assert extrair_placa([("XX", 0.9)])[0] is None
    assert extrair_placa([])[0] is None


def test_cpf_e_mascara_lgpd():
    assert validar_cpf("526.018.159-06") == "52601815906"
    with pytest.raises(ValueError):
        validar_cpf("52601815907")
    assert mascarar_cpf("12345678909") == "***.***.789-**"
    assert formatar_placa("ABC1234") == "ABC-1234"


class _ReconhecedorFalso(ReconhecedorPlaca):
    """Substitui YOLO/EasyOCR para testar o pipeline sem os modelos."""

    def detectar_placas(self, imagem):
        return [(10, 10, 90, 40, 0.9)]

    def ler_caracteres(self, recorte):
        return [("ABC", 0.8), ("1D23", 0.8)]


def test_pipeline_completo_com_modelos_simulados():
    import cv2

    ok, buf = cv2.imencode(".jpg", np.full((100, 100, 3), 128, dtype=np.uint8))
    leitura = _ReconhecedorFalso().reconhecer(buf.tobytes())
    assert leitura.placa == "ABC1D23" and leitura.confianca == pytest.approx(0.85) and leitura.bbox == (10, 10, 90, 40)


def test_imagem_corrompida_gera_erro_de_imagem():
    with pytest.raises(ErroImagem):
        _ReconhecedorFalso().reconhecer(b"isto nao e uma imagem")
