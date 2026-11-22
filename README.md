# <h1 align = "center"> **Projeto Integrador - AEGIS-LPR**  </h1>

<div align = "center">

<img src = "imgs\caput-README.png" alt = "" height = "400">

### Status do Projeto: Em Andamento (45%) 🚧

*Última Atualização em 21/11/2026*

</div>
<br>

## 🗂 Sumário

- [📝 Apresentação](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-apresenta%C3%A7%C3%A3o)
- [🎯 Objetivos do Projeto](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-objetivos-do-projeto)
- [⚙ Funcionalidades](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-funcionalidades)
    - [🚘 Reconhecimento de Placas](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-reconhecimento-de-placas)
    - [👥 Gerenciamento de Usuários e Veículos](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-gerenciamento-de-usu%C3%A1rios-e-ve%C3%ADculos)
    - [🔐 Controle de Acesso e Autenticação](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-controle-de-acesso-e-autentica%C3%A7%C3%A3o)
    - [📋 Histórico de Acessos](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-hist%C3%B3rico-de-acessos)
- [💻 Tecnologias Utilizadas](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-tecnologias-utilizadas)
- [🔨 Arquitetura do Back-End](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-arquitetura-do-back-end)
- [📂 Estrutura das Pastas](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-estrutura-das-pastas)
- [📃 Requisitos para Instalação](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-requisitos-para-instala%C3%A7%C3%A3o)
  - [🔹 Requisitos de Ambiente](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-requisitos-de-ambiente)
  - [🔹 Dependências da Aplicação](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-depend%C3%AAncias-da-aplica%C3%A7%C3%A3o)
  - [🔹 Dependências de Desenvolvimento e Testes](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-depend%C3%AAncias-de-desenvolvimento-e-testes)
- [🔑 Acesso e Clonagem do Projeto](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-acesso-e-clonagem-do-projeto)
- [💻 Criação do Ambiente Virtual](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-cria%C3%A7%C3%A3o-do-ambiente-virtual)
- [📥 Instalação das Dependências](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-instala%C3%A7%C3%A3o-das-depend%C3%AAncias)
- [⚙ Configuração das Variáveis de Ambiente](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-configura%C3%A7%C3%A3o-das-vari%C3%A1veis-de-ambiente)
- [💾 Configuração do Banco de Dados](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-configura%C3%A7%C3%A3o-do-banco-de-dados)
- [▶️ Abrir e Executar o Projeto](https://github.com/guilherme2W2/Aegis-lpr/tree/main#%EF%B8%8F-abrir-e-executar-o-projeto)
- [📡 Documentação dos Endpoints](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-documenta%C3%A7%C3%A3o-dos-endpoints)
- [📋 Regras de Negócio](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-regras-de-neg%C3%B3cio)
- [🗞 Licença](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-licen%C3%A7a)
- [👨🏻‍💻 Integrantes](https://github.com/guilherme2W2/Aegis-lpr/tree/main#%E2%80%8D-integrantes)
- [✨ Contatos & Referências](https://github.com/guilherme2W2/Aegis-lpr/tree/main#-contatos--refer%C3%AAncias)
<br>


## 📝 Apresentação

A **Segurança Pública** sempre está presente nas conversas do dia a dia. Seja na rua, no metrô, no trabalho ou até em casa com a família, comentários a respeito desse tema são recorrentes. Segundo o levantamento Nexus/BTG divulgado pelo portal [Metrópoles](https://www.metropoles.com/sao-paulo/seguranca-publica-eleicoes-2026), aproximadamente 30% dos brasileiros apontaram a segurança pública, a violência e a criminalidade como suas principais preocupações nacionais, seguidas pela corrupção (24%) e pela saúde (23%). Com o crescimento das áreas urbanas e a necessidade de aprimorar continuamente os mecanismos de segurança, soluções tecnológicas de automação apresentam oportunidades para tornar esse processo mais eficiente, organizado e rastreável.

É nesse contexto que a nossa equipe de desenvolvimento apresenta o **AEGIS-LPR (*License Plate Recognition*)**, um sistema inteligente de controle e automação de acesso veicular desenvolvido com o propósito de otimizar o gerenciamento de entradas e saídas em condomínios residenciais.

A solução utiliza tecnologias de processamento de imagens e reconhecimento óptico de caracteres (*OCR*) para identificar as placas de veículos e verificar sua autorização de acesso com base em registros previamente cadastrados. A partir dessa identificação, o sistema realiza a validação das informações, registra as movimentações e disponibiliza em um histórico de acessos para consulta e gerenciamento. 

Além da automatização do processo de identificação, o **AEGIS-LPR** busca proporcionar maior organização administrativa, rastreabilidade das movimentações e centralização das informações, contribuindo para uma gestão mais eficiente do controle de acesso veicular e atendendo às demandas de condomínios e conjuntos habitacionais, especialmente em grandes centros urbanos, como São Paulo.

O nosso projeto integra conhecimentos de **Engenharia da Computação**, especialmente nas áreas de desenvolvimento de software, integração de sistemas, processamento de imagens e gerenciamento de bancos de dados. Sua concepção e desenvolvimento fazem parte das atividades acadêmicas do curso de Bacharelado em Engenharia da Computação, conciliando a aplicação prática dos conhecimentos adquiridos com o desenvolvimento de uma solução tecnológica para um problema real.

> [!IMPORTANT]
> Por se tratar de um Projeto de Extensão e Aprendizado, o desenvolvimento da nossa aplicação será realizado de forma gradual, acompanhando a matriz curricular e as etapas previstas na grade do nosso curso. Por isso, cada semestre contemplará o desenvolvimento de uma parte específica do projeto, permitindo a aplicação prática dos conhecimentos adquiridos ao longo da graduação.
> Neste semestre, os trabalhos foram concentrados na estruturação e no desenvolvimento do Back-End. A conclusão da aplicação está prevista para dezembro de 2028.
<br>

## 🎯 Objetivos do Projeto

Este projeto tem por objetivo desenvolver um sistema inteligente de controle e automação para acesso veícular em residências, condomínios e conjuntos habitacionais. Foi utilizadas tecnologias de reconhecimento de placas, processamento de imagens e gerenciamento de bancos de dados. O sistema busca identificar veículos, verificar suas permissões de acesso e registrar suas movimentações, contribuindo para a organização e o gerenciamento. Para a finalidade de gerenciamento e controle, os objetivos foram separados em partes:

- a) Reconhecimento de placas: implementar mecanismos de processamento de imagens e reconhecimento óptico de caracteres (OCR) para identificar placas veiculares; ✔
- b) Gerenciamento de veículos e usuários: permitir o cadastro, a consulta, a atualização e a exclusão de informações de moradores, funcionários e veículos; ✔
- c) Validação de acesso: verificar se os veículos identificados possuem autorização para entrar no condomínio, de acordo com os registros cadastrados; ✔
- d) Registro de movimentações: armazenar informações sobre entradas e saídas, mantendo um histórico de acessos para consultas posteriores; ✔
- e) Gerenciamento de informações: centralizar os dados de usuários, veículos e movimentações em um banco de dados, garantindo sua organização e disponibilidade; ✔
- f) Desenvolvimento da API: estruturar uma interface de comunicação entre os componentes do sistema, permitindo a integração dos recursos de reconhecimento, validação e gerenciamento; ✔
- g) Confiabilidade do sistema: desenvolver e executar testes para verificar o funcionamento dos recursos implementados e a consistência das informações armazenadas. ✔
<br>

## ⚙ Funcionalidades

O AEGIS-LPR contará com esse conjunto de funcionalidades voltadas à identificação de veículos, ao gerenciamento de cadastros e ao controle de acesso em condomínios residenciais:

### 🚘 Reconhecimento de Placas

- Identificação das placas veiculares por meio do processamento de imagens;
- Detecção da região da placa utilizando modelos de visão computacional;
- Reconhecimento dos caracteres presentes na placa por meio de um OCR.

### 👥 Gerenciamento de Usuários e Veículos

- Cadastro de moradores e funcionários;
- Cadastro de veículos de diferentes modalidades de acordo com as necessidades de cada condomínio (Modalidade A e B inicialmente);
- Consulta e visualização dos veículos cadastrados;
- Atualização e exclusão de registros no histórico;
- Verificação da situação do veículo e de sua autorização de acesso.

### 🔐 Controle de Acesso e Autenticação

- Validação das placas reconhecidas;
- Verificação da autorização de entrada do veículo;
- Registro das tentativas de acesso, conforme o resultado da validação;
- Armazenamento das movimentações de entrada e saída;
- Autenticação de usuários para acesso aos recursos protegidos da API;
- Validação das informações recebidas pelo sistema.

### 📋 Histórico de Acessos

- Registro de data e horário das movimentações;
- Consultas aos registros de acesso;
- Identificação dos veículos envolvidos nas movimentações;
- Disponibilização do histórico para acompanhamento e gerenciamento;
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

## 🔑 Acesso e clonagem do projeto

*🚧 Em construção 🚧*
<br>


## 💻 Criação do ambiente virtual

*🚧 Em construção 🚧*
<br>


## 📥 Instalação das dependências

*🚧 Em construção 🚧*
<br>


## ⚙ Configuração das Variáveis de Ambiente

*🚧 Em construção 🚧*
<br>

## 💾 Configuração do Banco de Dados

*🚧 Em construção 🚧*
<br>


## ▶️ Abrir e Executar o Projeto

*🚧 Em construção 🚧*
<br>

## 📡 Documentação dos Endpoints

*🚧 Em construção 🚧*
<br>

## 📋 Regras de Negócio

*🚧 Em construção 🚧*
<br>

## 🗞 Licença

*🚧 Em construção 🚧*
<br>

## 👨🏻‍💻 Integrantes

*🚧 Em construção 🚧*
<br>

## ✨ Contatos & Referências

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
