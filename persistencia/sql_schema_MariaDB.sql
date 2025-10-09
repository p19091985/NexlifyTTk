-- MariaDB é altamente compatível com MySQL.
-- Este script cria o banco, o usuário e as tabelas para o ambiente MariaDB.

-- Etapa 1: Criar o banco de dados se ele não existir
CREATE DATABASE IF NOT EXISTS NexlifyTTk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Etapa 2: Criar o usuário e conceder permissões
-- NOTA: Use 'localhost' se a aplicação e o banco estiverem na mesma máquina.
-- Use '%' para permitir conexões de qualquer host.
CREATE USER IF NOT EXISTS 'gato'@'%' IDENTIFIED BY '-Vladmir!5Anos-';
/*
  Este comando irá alterar o usuário 'gato' existente ou criá-lo se não existir,
  permitindo que ele se conecte de qualquer host ('%').
  A senha e as permissões no banco de dados NexlifyTTk são mantidas.
*/

GRANT ALL PRIVILEGES ON NexlifyTTk.* TO 'gato'@'%' IDENTIFIED BY '-Vladmir!5Anos-';

-- Este comando aplica as novas permissões imediatamente sem precisar reiniciar o servidor.
FLUSH PRIVILEGES;

-- Etapa 3: Usar o banco de dados
USE NexlifyTTk;

-- Etapa 4: Limpeza e criação das tabelas (em ordem de dependência reversa)
DROP TABLE IF EXISTS LOG_ALTERACOES;
DROP TABLE IF EXISTS LINGUAGENS_PROGRAMACAO;
DROP TABLE IF EXISTS ESPECIE_GATOS;
DROP TABLE IF EXISTS TIPOS_LINGUAGEM;
DROP TABLE IF EXISTS USUARIOS;

-- Tabela de Usuários
CREATE TABLE USUARIOS (
    LOGIN_USUARIO VARCHAR(255) PRIMARY KEY NOT NULL,
    SENHA_CRIPTOGRAFADA VARCHAR(255) NOT NULL,
    NOME_COMPLETO VARCHAR(255) NOT NULL,
    TIPO_ACESSO VARCHAR(100) NOT NULL CHECK (TIPO_ACESSO IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);

-- Tabela de Tipos de Linguagem
CREATE TABLE TIPOS_LINGUAGEM (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Linguagens com Chave Estrangeira
CREATE TABLE LINGUAGENS_PROGRAMACAO (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100) NOT NULL,
    ID_TIPO INT,
    ANO_CRIACAO INT,
    CATEGORIA VARCHAR(100),
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_LINGUAGEM(ID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela de Log de Alterações
CREATE TABLE LOG_ALTERACOES (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    TIMESTAMP DATETIME NOT NULL,
    LOGIN_USUARIO VARCHAR(255),
    ACAO TEXT,
    FOREIGN KEY (LOGIN_USUARIO) REFERENCES USUARIOS(LOGIN_USUARIO) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela Especie Gatos
CREATE TABLE ESPECIE_GATOS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME_ESPECIE VARCHAR(255) NOT NULL UNIQUE,
    PAIS_ORIGEM VARCHAR(255),
    TEMPERAMENTO VARCHAR(255)
);

INSERT INTO USUARIOS (LOGIN_USUARIO, SENHA_CRIPTOGRAFADA, NOME_COMPLETO, TIPO_ACESSO) VALUES
('admin', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Usuário Administrador', 'Administrador Global'),
('diretor.op', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Carlos Diretor', 'Diretor de Operações'),
('gerente.ti', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Beatriz Gerente', 'Gerente de TI'),
('ana.supervisor', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Ana Supervisora', 'Supervisor de Produção'),
('bruno.operador', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Bruno Operador', 'Operador de Linha'),
('carla.analista', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Carla Analista', 'Analista de Dados'),
('davi.auditor', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Davi Auditor', 'Auditor Externo'),
('elisa.op', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Elisa Operadora', 'Operador de Linha'),
('felipe.gerente', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Felipe Gerente TI', 'Gerente de TI'),
('gabi.analista', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Gabriela Analista', 'Analista de Dados'),
('hugo.diretor', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Hugo Diretor', 'Diretor de Operações'),
('isa.supervisor', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Isadora Supervisora', 'Supervisor de Produção'),
('joao.operador', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'João Operador', 'Operador de Linha'),
('lara.admin', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Lara Administradora', 'Administrador Global'),
('mateus.auditor', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Mateus Auditor', 'Auditor Externo');

INSERT INTO TIPOS_LINGUAGEM (NOME) VALUES ('Estática'), ('Dinâmica'), ('Mista'), ('Funcional'), ('Lógica');

INSERT INTO LINGUAGENS_PROGRAMACAO (NOME, ID_TIPO, ANO_CRIACAO, CATEGORIA) VALUES
('C++', 1, 1985, 'Linguagens Compiladas'),
('Java', 1, 1995, 'Linguagens Compiladas'),
('Rust', 1, 2010, 'Linguagens Compiladas'),
('Python', 2, 1991, 'Linguagens Interpretadas'),
('JavaScript', 2, 1995, 'Linguagens Interpretadas');

INSERT INTO ESPECIE_GATOS (NOME_ESPECIE, PAIS_ORIGEM, TEMPERAMENTO) VALUES
('Siamês', 'Tailândia', 'Inteligente e Afetuoso'),
('Persa', 'Irã (Pérsia)', 'Calmo e Dócil'),
('Maine Coon', 'Estados Unidos', 'Gentil e Brincalhão'),
('Bengal', 'Estados Unidos', 'Ativo e Curioso');