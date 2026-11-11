"""Regras de validação reutilizadas pelos schemas e serviços (somente stdlib)."""
import re
from typing import Optional

from app.utils.formatacao import somente_digitos

REGEX_PLACA = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")  # antiga (ABC1234) e Mercosul (ABC1D23)
REGEX_PLACA_BUSCA = re.compile(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}")
REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Confusões típicas de OCR, corrigidas conforme a posição do caractere na placa
_NUM_PARA_LETRA = {"0": "O", "1": "I", "2": "Z", "5": "S", "6": "G", "8": "B"}
_LETRA_PARA_NUM = {"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1", "Z": "2", "S": "5", "G": "6", "B": "8"}


def validar_cpf(valor: str) -> str:
    cpf = somente_digitos(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValueError("CPF inválido")
    for i in (9, 10):
        soma = sum(int(cpf[n]) * (i + 1 - n) for n in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            raise ValueError("CPF inválido")
    return cpf


def validar_email(valor: str) -> str:
    email = (valor or "").strip().lower()
    if len(email) > 150 or not REGEX_EMAIL.match(email):
        raise ValueError("E-mail inválido")
    return email


def validar_telefone(valor: str) -> str:
    digitos = somente_digitos(valor)
    if len(digitos) not in (10, 11, 12, 13):
        raise ValueError("Telefone inválido (informe DDD + número)")
    return digitos


def validar_nome_completo(valor: str) -> str:
    nome = " ".join((valor or "").split())
    if len(nome.split(" ")) < 2:
        raise ValueError("Informe o nome completo")
    return nome


def validar_senha_forte(valor: str) -> str:
    if len(valor) < 8 or len(valor) > 128:
        raise ValueError("A senha deve ter entre 8 e 128 caracteres")
    if not re.search(r"[A-Za-z]", valor) or not re.search(r"\d", valor):
        raise ValueError("A senha deve conter letras e números")
    return valor


def normalizar_placa(texto: Optional[str]) -> str:
    return re.sub(r"[^A-Z0-9]", "", (texto or "").upper())


def placa_valida(placa: str) -> bool:
    return bool(REGEX_PLACA.match(placa or ""))


def corrigir_placa(texto: Optional[str]) -> Optional[str]:
    """Normaliza e corrige confusões letra/número do OCR. Retorna None se não for uma placa."""
    p = normalizar_placa(texto)
    if len(p) != 7:
        return None
    resultado = []
    for pos, c in enumerate(p):
        if pos < 3:
            c = _NUM_PARA_LETRA.get(c, c)
        elif pos in (3, 5, 6):
            c = _LETRA_PARA_NUM.get(c, c)
        resultado.append(c)
    candidata = "".join(resultado)
    return candidata if placa_valida(candidata) else None


def validar_placa_entrada(valor: str) -> str:
    """Usada nos schemas: aceita 'abc-1234', 'ABC1D23' etc. e devolve normalizada."""
    placa = normalizar_placa(valor)
    if not placa_valida(placa):
        raise ValueError("Placa inválida (use ABC1234 ou ABC1D23)")
    return placa
