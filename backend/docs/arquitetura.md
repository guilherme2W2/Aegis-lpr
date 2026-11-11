# Arquitetura — AEGIS-LPR

Sistema de automação de portão por leitura de placa (LPR), operando **100% em rede local**.

## Visão geral

```
 Câmera IP ──(foto/evento + X-Camera-Key)──▶ ┌─────────────────────────────┐
                                             │  API FastAPI (Uvicorn)      │
 App/Web (Morador, Porteiro, Admin) ──JWT──▶ │  routers → services → models│──▶ MySQL
                                             └──────────────┬──────────────┘
                                                            │ pulso HTTP (LAN)
                                                            ▼
                                             Microcontrolador + Relé ──▶ Motor do portão
```

## Camadas (`app/`)

| Camada | Responsabilidade |
|---|---|
| `main.py` | Cria a app, middleware de **bloqueio fora da LAN**, logs, seed do Super ADM, agendador do job de limpeza. |
| `database.py` | Engine SQLAlchemy (PyMySQL), sessão e `Base`. Lê o `.env`. |
| `security.py` | Hash de senha (PBKDF2), JWT HS256, RBAC (`exigir_papeis`), chave da câmera, limitador de login, checagem de IP local. |
| `models/` | Tabelas: `usuarios`, `veiculos`, `acessos` (log de auditoria). |
| `schemas/` | Contratos Pydantic de entrada/saída e validações (CPF, placa, e-mail, senha). |
| `routers/` | Endpoints HTTP. Apenas orquestram: validam permissão e chamam services. |
| `services/reconhecimento.py` | OpenCV → YOLO (localiza a placa) → EasyOCR (lê os caracteres) → correção por posição. **Não decide acesso.** |
| `services/controle_acesso.py` | Decide liberar/negar, aciona o relé, grava o log, regras de visitante (limite, 48h) e job de limpeza. |
| `services/validacao.py` | Regras puras (CPF, placa Mercosul/antiga, senha). |
| `utils/formatacao.py` | Máscara de CPF (LGPD), formatação de placa/telefone, datas em UTC, escape de CSV. |

## Fluxo de uma leitura automática

1. A câmera envia a imagem (`POST /acessos/lpr/imagem`) ou o texto da placa (`/acessos/lpr/placa`) com `X-Camera-Key`.
2. `reconhecimento.py` detecta a placa (YOLO), lê os caracteres (EasyOCR) e normaliza.
3. `controle_acesso.processar_leitura` valida: placa cadastrada → status `ATIVO` → visitante dentro do prazo → morador responsável ativo.
4. Se válido, aciona o relé (pulso). **Qualquer falha** (placa ilegível, não cadastrada, desativada, relé fora do ar) mantém o portão fechado e gera log.
5. O resultado fica em `acessos` (placa, motivo, origem, confiança, operador quando manual).

## Decisões de projeto

- **Dependências mínimas**: JWT e hash de senha usam apenas `hmac`/`hashlib` da biblioteca padrão; e-mail usa `smtplib`; acionamento HTTP do relé usa `urllib`. Só foram usadas as bibliotecas pedidas (+ `cryptography` exigida pelo PyMySQL e `pytest`/`httpx` para testes).
- **Datas em UTC** no banco e nas respostas. O job diário usa o horário local do servidor.
- **Histórico preservado**: ao apagar um veículo, `acessos.veiculo_id` vira `NULL`, mas a placa continua gravada no log.
- **Modelos pesados sob demanda**: YOLO e EasyOCR só carregam na primeira leitura, então a API sobe mesmo sem eles.
- **Execução**: use **1 worker** do Uvicorn (o agendador do job e o limitador de login ficam em memória do processo).
