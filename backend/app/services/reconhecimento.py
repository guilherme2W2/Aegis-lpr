"""Leitura de placas: OpenCV (imagem) -> YOLO (localiza a placa) -> EasyOCR (lê os caracteres).

Bibliotecas pesadas são importadas sob demanda, então o restante da API sobe mesmo sem elas.
Este módulo NÃO decide nada sobre acesso: apenas devolve a placa lida (separação de responsabilidades).
"""
import logging
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from app.services.validacao import REGEX_PLACA_BUSCA, corrigir_placa, normalizar_placa

logger = logging.getLogger("aegis.reconhecimento")

CARACTERES_PERMITIDOS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class ErroReconhecimento(Exception):
    """Falha de infraestrutura (modelo ausente, biblioteca não instalada...)."""


class ErroImagem(Exception):
    """A imagem recebida é inválida/corrompida."""


@dataclass
class LeituraPlaca:
    placa: Optional[str]
    confianca: float
    bbox: Optional[tuple] = None
    texto_bruto: Optional[str] = None


def extrair_placa(fragmentos: list[tuple[str, float]]) -> tuple[Optional[str], float]:
    """Procura uma placa válida nos fragmentos de texto do OCR (ordenados da esquerda p/ direita)."""
    limpos = [(normalizar_placa(t), c) for t, c in fragmentos if normalizar_placa(t)]
    if not limpos:
        return None, 0.0

    # 1) algum fragmento sozinho já é a placa
    for texto, conf in limpos:
        placa = corrigir_placa(texto)
        if placa:
            return placa, conf

    # 2) junta tudo (ex.: placa Mercosul com a palavra BRASIL ou OCR dividido em partes)
    junto = "".join(t for t, _ in limpos)
    media = sum(c for _, c in limpos) / len(limpos)
    achado = REGEX_PLACA_BUSCA.search(junto)
    if achado:
        return achado.group(0), media
    placa = corrigir_placa(junto)
    if placa:
        return placa, media
    return None, media


class ReconhecedorPlaca:
    def __init__(self) -> None:
        self.caminho_modelo = os.getenv("YOLO_MODEL_PATH", "modelos/placa.pt")
        self.conf_deteccao = float(os.getenv("YOLO_CONFIANCA_MINIMA", "0.35"))
        self.conf_minima = float(os.getenv("OCR_CONFIANCA_MINIMA", "0.40"))
        self.usar_gpu = os.getenv("USAR_GPU", "false").lower() == "true"
        self._yolo = None
        self._leitor = None

    # ------------------------------------------------------------ carregamento sob demanda
    def _carregar_yolo(self):
        if self._yolo is None:
            if not os.path.isfile(self.caminho_modelo):
                raise ErroReconhecimento(
                    f"Modelo YOLO não encontrado em '{self.caminho_modelo}'. Veja YOLO_MODEL_PATH no README."
                )
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise ErroReconhecimento("Biblioteca 'ultralytics' não instalada") from exc
            self._yolo = YOLO(self.caminho_modelo)
        return self._yolo

    def _carregar_ocr(self):
        if self._leitor is None:
            try:
                import easyocr
            except ImportError as exc:
                raise ErroReconhecimento("Biblioteca 'easyocr' não instalada") from exc
            pasta = os.getenv("EASYOCR_DIR") or None  # modelos pré-baixados (operação 100% offline)
            baixar = os.getenv("EASYOCR_DOWNLOAD", "true").lower() == "true"
            self._leitor = easyocr.Reader(
                ["en"], gpu=self.usar_gpu, model_storage_directory=pasta, download_enabled=baixar, verbose=False
            )
        return self._leitor

    # ------------------------------------------------------------ etapas do pipeline
    def decodificar_imagem(self, dados: bytes):
        import cv2
        import numpy as np

        imagem = cv2.imdecode(np.frombuffer(dados, dtype=np.uint8), cv2.IMREAD_COLOR)
        if imagem is None:
            raise ErroImagem("Não foi possível decodificar a imagem enviada")
        return imagem

    def detectar_placas(self, imagem) -> list[tuple[int, int, int, int, float]]:
        """YOLO: devolve caixas (x1, y1, x2, y2, confiança)."""
        modelo = self._carregar_yolo()
        caixas = []
        for resultado in modelo.predict(imagem, conf=self.conf_deteccao, verbose=False):
            for caixa in resultado.boxes:
                x1, y1, x2, y2 = (int(v) for v in caixa.xyxy[0].tolist())
                caixas.append((x1, y1, x2, y2, float(caixa.conf[0])))
        return caixas

    def preprocessar(self, recorte):
        import cv2

        cinza = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
        if cinza.shape[0] < 80:  # amplia placas pequenas para ajudar o OCR
            fator = 80 / max(cinza.shape[0], 1)
            cinza = cv2.resize(cinza, None, fx=fator, fy=fator, interpolation=cv2.INTER_CUBIC)
        return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(cinza)

    def ler_caracteres(self, recorte) -> list[tuple[str, float]]:
        """EasyOCR: devolve [(texto, confiança)] ordenado da esquerda para a direita."""
        leitor = self._carregar_ocr()
        brutos = leitor.readtext(self.preprocessar(recorte), allowlist=CARACTERES_PERMITIDOS, detail=1)
        brutos.sort(key=lambda r: min(p[0] for p in r[0]))
        return [(texto, float(conf)) for _, texto, conf in brutos]

    # ------------------------------------------------------------ API do serviço
    def reconhecer(self, dados_imagem: bytes) -> LeituraPlaca:
        imagem = self.decodificar_imagem(dados_imagem)
        altura, largura = imagem.shape[:2]
        melhor: Optional[LeituraPlaca] = None

        for x1, y1, x2, y2, conf_det in sorted(self.detectar_placas(imagem), key=lambda c: c[4], reverse=True):
            margem = 4
            recorte = imagem[max(y1 - margem, 0):min(y2 + margem, altura), max(x1 - margem, 0):min(x2 + margem, largura)]
            if recorte.size == 0:
                continue
            fragmentos = self.ler_caracteres(recorte)
            placa, conf_ocr = extrair_placa(fragmentos)
            if not placa:
                continue
            leitura = LeituraPlaca(
                placa=placa,
                confianca=round((conf_det + conf_ocr) / 2, 3),
                bbox=(x1, y1, x2, y2),
                texto_bruto=" ".join(t for t, _ in fragmentos),
            )
            if melhor is None or leitura.confianca > melhor.confianca:
                melhor = leitura

        if melhor is None:
            return LeituraPlaca(placa=None, confianca=0.0)
        if melhor.confianca < self.conf_minima:
            logger.info("Leitura descartada por baixa confiança: %s (%.2f)", melhor.placa, melhor.confianca)
            return LeituraPlaca(None, melhor.confianca, melhor.bbox, melhor.texto_bruto)
        return melhor


@lru_cache(maxsize=1)
def obter_reconhecedor() -> ReconhecedorPlaca:
    return ReconhecedorPlaca()
