# <h1 align = "center"> **Projeto Integrador - AEGIS-LPR**  </h1>

<div align = "center">

<img src = "imgs\caput-README.png" alt = "" height = "400">

</div>

### Status do Projeto: Em Andamento (45%) 🚧

*Última Atualização em 20/11/2026*
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

![Python](https://img.shields.io/badge/Python-0?style=for-the-badge&logo=python&logoColor=%23FFFFFF&color=%233776AB)
![Git](https://img.shields.io/badge/Git-0?style=for-the-badge&logo=git&logoColor=%23FFFFFF&color=%23F05032)
![GitHub](https://img.shields.io/badge/GitHub-0?style=for-the-badge&logo=github&logoColor=%23FFFFFF&color=%23181717) <br>
<br>


## Arquitetura do Back-End

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

## Requisitos para Instalação

- Python 3.10+
- MySQL 8 (ou MariaDB) — ou SQLite apenas para desenvolvimento
- Um **modelo YOLO de detecção de placas** (`.pt`) — não incluído no repositório (veja abaixo)

# --- API ---
fastapi>=0.110
uvicorn[standard]>=0.29
pydantic>=2.6

# --- Banco de dados ---
SQLAlchemy>=2.0
PyMySQL>=1.1
cryptography>=42        # exigido pelo PyMySQL para autenticação do MySQL 8 (caching_sha2_password)

# --- Configuração ---
python-dotenv>=1.0

# --- Visão computacional / LPR ---
opencv-python>=4.9
ultralytics>=8.1        # YOLO (instala PyTorch)
easyocr>=1.7

# --- Testes (desenvolvimento) ---
pytest>=8.0
httpx>=0.27             # exigido pelo TestClient do FastAPI

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

## Integrantes

*🚧 Em construção 🚧*
<br>

## 👨🏻‍💻 Contatos & Referências

*🚧 Em construção 🚧*

## Licença

*🚧 Em construção 🚧*
<br>

Copyright ©️ 2026 - AEGIS-LPR - BRAZIL