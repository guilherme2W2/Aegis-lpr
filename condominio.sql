-- ============================================================
-- Projeto Integrador - Sistema de Condomínio (LPR)
-- Script de criação do banco de dados (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS condominio
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE condominio;

-- ------------------------------------------------------------
-- Módulo de Unidades Habitacionais
-- ------------------------------------------------------------

CREATE TABLE blocos_setores (
    id_bloco    INT AUTO_INCREMENT PRIMARY KEY,
    nome_bloco  VARCHAR(50)  NOT NULL,
    descricao   VARCHAR(100)
);

CREATE TABLE residencias (
    id_residencia   INT AUTO_INCREMENT PRIMARY KEY,
    numero_unidade  VARCHAR(20) NOT NULL,
    quantidade_vaga INT,
    id_bloco        INT NOT NULL,
    CONSTRAINT fk_residencias_bloco
        FOREIGN KEY (id_bloco) REFERENCES blocos_setores (id_bloco)
);

-- ------------------------------------------------------------
-- Módulo de Cadastros e Acessos
-- ------------------------------------------------------------

CREATE TABLE moradores (
    id_morador    INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    cpf           VARCHAR(14)  NOT NULL UNIQUE,
    celular       VARCHAR(15),
    tipo_morador  VARCHAR(30),
    id_residencia INT NOT NULL,
    CONSTRAINT fk_moradores_residencia
        FOREIGN KEY (id_residencia) REFERENCES residencias (id_residencia)
);

CREATE TABLE usuarios_sistema (
    id_usuario   INT AUTO_INCREMENT PRIMARY KEY,
    login        VARCHAR(50)  NOT NULL UNIQUE,
    senha_hash   VARCHAR(255) NOT NULL,
    nivel_acesso VARCHAR(20),
    id_morador   INT UNIQUE,
    CONSTRAINT fk_usuarios_morador
        FOREIGN KEY (id_morador) REFERENCES moradores (id_morador)
);

CREATE TABLE contatos_emergencia (
    id_contato        INT AUTO_INCREMENT PRIMARY KEY,
    nome_contato      VARCHAR(100) NOT NULL,
    telefone          VARCHAR(15),
    parentesco_vinculo VARCHAR(50),
    id_morador        INT NOT NULL,
    CONSTRAINT fk_contatos_morador
        FOREIGN KEY (id_morador) REFERENCES moradores (id_morador)
);

-- ------------------------------------------------------------
-- Módulo de Gestão de Veículos
-- ------------------------------------------------------------

CREATE TABLE veiculos_moradores (
    id_veiculo    INT AUTO_INCREMENT PRIMARY KEY,
    placa         VARCHAR(10) NOT NULL UNIQUE,
    marca_modelo  VARCHAR(50),
    cor           VARCHAR(30),
    id_residencia INT NOT NULL,
    CONSTRAINT fk_veiculos_residencia
        FOREIGN KEY (id_residencia) REFERENCES residencias (id_residencia)
);

CREATE TABLE documentos_veiculos (
    id_documento   INT AUTO_INCREMENT PRIMARY KEY,
    numero_renavam VARCHAR(15),
    status_legal   VARCHAR(20),
    id_veiculo     INT NOT NULL UNIQUE,
    CONSTRAINT fk_documentos_veiculo
        FOREIGN KEY (id_veiculo) REFERENCES veiculos_moradores (id_veiculo)
);

-- ------------------------------------------------------------
-- Módulo de Visitantes e Externos
-- ------------------------------------------------------------

CREATE TABLE visitantes_prestadores (
    id_externo      INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    rg_cpf          VARCHAR(20),
    empresa_vinculo VARCHAR(50),
    telefone        VARCHAR(15)
);

CREATE TABLE agendamento_acesso (
    id_agendamento   INT AUTO_INCREMENT PRIMARY KEY,
    data_reserva     DATE NOT NULL,
    hora_limite_inicio TIME,
    hora_limite_fim  TIME,
    placa_visitante  VARCHAR(10),
    id_residencia    INT NOT NULL,
    id_externo       INT NOT NULL,
    CONSTRAINT fk_agendamento_residencia
        FOREIGN KEY (id_residencia) REFERENCES residencias (id_residencia),
    CONSTRAINT fk_agendamento_externo
        FOREIGN KEY (id_externo) REFERENCES visitantes_prestadores (id_externo)
);

-- ------------------------------------------------------------
-- Módulo de Automação e Validação LPR
-- ------------------------------------------------------------

CREATE TABLE dispositivos_hardware (
    id_dispositivo    INT AUTO_INCREMENT PRIMARY KEY,
    nome_equipamento  VARCHAR(50) NOT NULL,
    tipo_hardware     VARCHAR(30),
    ip_dispositivo    VARCHAR(15),
    status_operacional VARCHAR(20)
);

CREATE TABLE historico_acessos (
    id_acesso             INT AUTO_INCREMENT PRIMARY KEY,
    data_hora             DATETIME NOT NULL,
    placa_capturada       VARCHAR(10),
    resultado_autenticacao VARCHAR(20),
    id_dispositivo        INT NOT NULL,
    CONSTRAINT fk_historico_dispositivo
        FOREIGN KEY (id_dispositivo) REFERENCES dispositivos_hardware (id_dispositivo)
);

CREATE TABLE alertas_seguranca (
    id_alerta          INT AUTO_INCREMENT PRIMARY KEY,
    data_hora_alerta   DATETIME NOT NULL,
    tipo_alerta        VARCHAR(50),
    nivel_criticidade  VARCHAR(15),
    descricao_ocorrencia TEXT,
    id_acesso          INT NOT NULL,
    CONSTRAINT fk_alertas_acesso
        FOREIGN KEY (id_acesso) REFERENCES historico_acessos (id_acesso)
);
