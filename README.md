# AEGIS-LPR

Automação de portão por **reconhecimento de placas (LPR)** com controle de acesso por perfis, operando 100% em rede local.

**Stack:** FastAPI · Uvicorn · SQLAlchemy · PyMySQL · python-dotenv · Pydantic · OpenCV · EasyOCR · Ultralytics (YOLO)

## Requisitos

- Python 3.10+
- MySQL 8 (ou MariaDB) — ou SQLite apenas para desenvolvimento
- Um **modelo YOLO de detecção de placas** (`.pt`) — não incluído no repositório (veja abaixo)

## Instalação

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # e edite os valores
```

Crie o banco (MySQL):

```sql
CREATE DATABASE aegis_lpr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aegis'@'%' IDENTIFIED BY 'sua-senha';
GRANT ALL ON aegis_lpr.* TO 'aegis'@'%';
```

As tabelas são criadas automaticamente na primeira execução, junto com o **Super ADM** definido em `SUPER_ADMIN_*` no `.env` (troca de senha obrigatória no primeiro login).

> O `.env` que acompanha o projeto usa SQLite e segredos de desenvolvimento. **Gere novos segredos e nunca versione o `.env`.**

## Executando

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000        # em produção: --host <IP da rede interna>, 1 worker
```

Swagger: http://localhost:8000/docs

## Modelos de IA

- **YOLO**: coloque seus pesos em `modelos/placa.pt` (ou ajuste `YOLO_MODEL_PATH`). É necessário um modelo treinado para detectar placas veiculares.
- **EasyOCR**: baixa os modelos de inglês na primeira execução. Para operar sem internet, copie a pasta de modelos para `EASYOCR_DIR` e use `EASYOCR_DOWNLOAD=false`.
- Sem GPU, a leitura roda em CPU (mais lenta). Ative `USAR_GPU=true` se houver CUDA.

## Testes

```bash
pytest -v
```

Usam SQLite em memória e simulam YOLO/EasyOCR/relé, então não exigem MySQL, GPU nem hardware.

## Documentação

- [`docs/arquitetura.md`](docs/arquitetura.md) — camadas, fluxo e decisões de projeto
- [`docs/controle_acesso.md`](docs/controle_acesso.md) — perfis, ciclo de visitantes, relé e fallback
- [`docs/endpoints.md`](docs/endpoints.md) — referência da API

## Segurança (resumo)

Acesso somente pela LAN (`SOMENTE_LAN`), JWT com expiração, senha temporária com troca obrigatória, bloqueio de login por tentativas, CPF mascarado (LGPD), câmera autenticada por chave, relé acionado por pulso (nunca "aberto contínuo") e auditoria completa em `acessos`.
