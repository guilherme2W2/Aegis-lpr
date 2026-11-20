# <h1 align = "center"> **Projeto Integrador - AEGIS-LPR**  </h1>

<div align = "center">

<img src = "imgs\caput-README.png" alt = "" height = "400">

### Status do Projeto: Em Andamento (45%) 🚧

*Última Atualização em 20/11/2026*

</div>
<br>

## 🗂 Sumário

<!-- - [📝 Descrição do Projeto](https://github.com/Victor-M-S-Rodrigues07/Projeto_Sabor_Express_POO___Projeto_N3-2026#-descri%C3%A7%C3%A3o-do-projeto) -->

*🚧 Em construção 🚧*
<br>


## 📝 Apresentação

A **Segurança Pública** sempre está presente nas conversas do dia a dia. Seja na rua, no metrô, no trabalho ou até em casa com a família, comentários a respeito desse tema são recorrentes. Segundo o levantamento Nexus/BTG divulgado pelo portal [Metrópoles](https://www.metropoles.com/sao-paulo/seguranca-publica-eleicoes-2026), aproximadamente 30% dos brasileiros apontaram a segurança pública, a violência e a criminalidade como suas principais preocupações nacionais, seguidas pela corrupção (24%) e pela saúde (23%). Com o crescimento das áreas urbanas e a necessidade de aprimorar continuamente os mecanismos de segurança, soluções tecnológicas de automação apresentam oportunidades para tornar esse processo mais eficiente, organizado e rastreável.

É nesse contexto que a nossa equipe de desenvolvimento apresenta o **AEGIS-LPR (*License Plate Recognition*)**, um sistema inteligente de controle e automação de acesso veicular desenvolvido com o propósito de otimizar o gerenciamento de entradas e saídas em condomínios residenciais.

A solução utiliza tecnologias de processamento de imagens e reconhecimento óptico de caracteres (*OCR*) para identificar as placas de veículos e verificar sua autorização de acesso com base em registros previamente cadastrados. A partir dessa identificação, o sistema realiza a validação das informações, registra as movimentações e disponibiliza em um histórico de acessos para consulta e gerenciamento. 

Além da automatização do processo de identificação, o **AEGIS-LPR** busca proporcionar maior organização administrativa, rastreabilidade das movimentações e centralização das informações, contribuindo para uma gestão mais eficiente do controle de acesso veicular e atendendo às demandas de condomínios e conjuntos habitacionais, especialmente em grandes centros urbanos, como São Paulo.

O nosso projeto integra conhecimentos de **Engenharia da Computação**, especialmente nas áreas de desenvolvimento de software, integração de sistemas, processamento de imagens e gerenciamento de bancos de dados. Sua concepção e desenvolvimento fazem parte das atividades acadêmicas do curso de Bacharelado em Engenharia da Computação, conciliando a aplicação prática dos conhecimentos adquiridos com o desenvolvimento de uma solução tecnológica para um problema real.
<br>

## 🎯 Objetivos do Projeto

*🚧 Em construção 🚧*
<br>


## ⚙ Funcionalidades do Projeto

*🚧 Em construção 🚧*
<br>


## 💻 Tecnologias Utilizadas

*🚧 Em construção 🚧*
<br>

<!-- ![Python](https://img.shields.io/badge/Python-0?style=for-the-badge&logo=python&logoColor=%23FFFFFF&color=%233776AB)
![Git](https://img.shields.io/badge/Git-0?style=for-the-badge&logo=git&logoColor=%23FFFFFF&color=%23F05032)
![GitHub](https://img.shields.io/badge/GitHub-0?style=for-the-badge&logo=github&logoColor=%23FFFFFF&color=%23181717)
<br> -->


## 🔨 Arquitetura do Back-End

*🚧 Em construção 🚧*
<br>


## 📂 Estrutura das Pastas

```
/backend

    /app
        /core
            config.py
            description.md

        /database
            database.py
            description.md
            session.py

        /models
            __init__.py
            acesso.py
            description.md
            usuario.py
            veiculo.py

        /repositories
            description.md

        /routers
            __init__.py
            acessor.py
            autenticacao.py
            description.md
            usuarios.py
            veiculos.py

        /schemas
            __init__.py
            acesso.py
            autenticacao.py
            description.md
            usuario.py
            veiculo.py

        /services
            __init__.py
            controle_acesso.py
            description.md
            reconhecimento,py
            validacao.py

        /utils
            __init__.py
            formatacao.py

        __init__.py
        AEGIS-LPR - Atalho.lnk
        database.py
        main.py
        security.py

        /venv

/docs
    arquitetura.md
    controle_acesso.md
    endpoints.md

/imgs

/tests
    __init__.py
    test_acessos.py        
    test_reconhecimento.py
    test_usuarios.py
    test_veiculos.py

.env.example
.gitignore
condominio.sql
README.md
requirements.txt
```
<br>

## 📃 Requisitos para Instalação

*Para executar o AEGIS-LPR, é necessário possuir os seguintes recursos e ferramentas instalados:*

### 🔹 Requisitos de Ambiente

- **Python:** versão 3.10 ou superior.
- **Banco de Dados:** MySQL 8 ou MariaDB, conforme a configuração adotada.
- **Modelo YOLO:** modelo de detecção de placas no formato `.pt`, necessário para o processamento e reconhecimento das imagens. 

> [!NOTE]
> O arquivo do YOLO não está incluído diretamente no repositório.

### 🔹 Dependências da Aplicação

As bibliotecas utilizadas no desenvolvimento e na execução do backend estão relacionadas no arquivo `requirements.txt`, incluindo:

- **FastAPI:** construção da API.
- **Uvicorn:** execução do servidor ASGI.
- **Pydantic:** validação e estruturação dos dados.
- **SQLAlchemy:** gerenciamento da comunicação com o banco de dados por meio de ORM.
- **PyMySQL:** conexão com o banco de dados MySQL.
- **cryptography:** suporte criptográfico para autenticação na conexão com o MySQL.
- **python-dotenv:** gerenciamento das variáveis de ambiente.
- **OpenCV:** processamento e manipulação de imagens.
- **Ultralytics:** execução do modelo YOLO para detecção de placas.
- **EasyOCR:** reconhecimento óptico dos caracteres das placas.

### 🔹 Dependências de Desenvolvimento e Testes

- **pytest:** execução e gerenciamento dos testes.
- **httpx:** suporte às requisições HTTP utilizadas nos testes da API.

> A instalação das dependências será realizada conforme as instruções disponíveis na seção Instalação das Dependências.
<br>

## Acesso e clonagem do projeto;

*🚧 Em construção 🚧*
<br>


## Criação do ambiente virtual;

*🚧 Em construção 🚧*
<br>


## Instalação das dependências;

*🚧 Em construção 🚧*
<br>


## Configuração das Variáveis de Ambiente

*🚧 Em construção 🚧*
<br>

## Configuração do Banco de Dados

*🚧 Em construção 🚧*
<br>


## ▶️ Abrir e Executar o Projeto

*🚧 Em construção 🚧*
<br>

## Documentação dos Endpoints

*🚧 Em construção 🚧*
<br>

## Regras de Negócio

*🚧 Em construção 🚧*
<br>

## Licença

*🚧 Em construção 🚧*
<br>

## Integrantes

*🚧 Em construção 🚧*
<br>

## 👨🏻‍💻 Contatos & Referências

*🚧 Em construção 🚧*

Copyright ©️ 2026 - AEGIS-LPR - BRAZIL

<!-- # AEGIS-LPR

Automação de portão por **reconhecimento de placas (LPR)** com controle de acesso por perfis, operando 100% em rede local.

**Stack:** FastAPI · Uvicorn · SQLAlchemy · PyMySQL · python-dotenv · Pydantic · OpenCV · EasyOCR · Ultralytics (YOLO)

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

Acesso somente pela LAN (`SOMENTE_LAN`), JWT com expiração, senha temporária com troca obrigatória, bloqueio de login por tentativas, CPF mascarado (LGPD), câmera autenticada por chave, relé acionado por pulso (nunca "aberto contínuo") e auditoria completa em `acessos`. -->
