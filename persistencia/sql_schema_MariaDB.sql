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
DROP TABLE IF EXISTS VEGETAIS;
DROP TABLE IF EXISTS TIPOS_VEGETAIS;
DROP TABLE IF EXISTS USUARIOS;
DROP TABLE IF EXISTS ESPECIE_GATOS;

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

-- Tabela de Tipos de Vegetais
CREATE TABLE TIPOS_VEGETAIS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Vegetais com Chave Estrangeira
CREATE TABLE VEGETAIS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100) NOT NULL,
    ID_TIPO INT,
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_VEGETAIS(ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
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

INSERT INTO TIPOS_VEGETAIS (NOME) VALUES ('Raízes e Tubérculos'), ('Folhas'), ('Flores e Inflorescências'), ('Frutos'), ('Legumes');

INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES
('Abóbora', 4), ('Abobrinha', 4), ('Agrião', 2), ('Aipim', 1), ('Alface', 2), ('Alho', 1), ('Almeirão', 2),
('Batata-doce', 1), ('Batata', 1), ('Berinjela', 4), ('Beterraba', 1), ('Brócolis', 3), ('Cebola', 1),
('Cenoura', 1), ('Chuchu', 4), ('Coentro', 2), ('Couve', 2), ('Couve-flor', 3), ('Ervilha', 5), ('Espinafre', 2),
('Feijão-vagem', 5), ('Inhame', 1), ('Jiló', 4), ('Maxixe', 4), ('Milho', 4), ('Pepino', 4), ('Pimentão', 4),
('Quiabo', 4), ('Rabanete', 1), ('Repolho', 2);

INSERT INTO ESPECIE_GATOS (NOME_ESPECIE, PAIS_ORIGEM, TEMPERAMENTO) VALUES
('Siamês', 'Tailândia', 'Inteligente e Afetuoso'),
('Persa', 'Irã (Pérsia)', 'Calmo e Dócil'),
('Maine Coon', 'Estados Unidos', 'Gentil e Brincalhão'),
('Bengal', 'Estados Unidos', 'Ativo e Curioso');


-- MariaDB é altamente compatível com MySQL.
-- Este script cria o banco, o usuário e as tabelas para o ambiente MariaDB.

-- Etapa 1: Criar o banco de dados se ele não existir
CREATE DATABASE IF NOT EXISTS NexlifyTTk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Etapa 2: Criar o usuário e conceder permissões
-- NOTA: Use 'localhost' se a aplicação e o banco estiverem na mesma máquina.
-- Use '%' para permitir conexões de qualquer host.
CREATE USER IF NOT EXISTS 'gato'@'%' IDENTIFIED BY '-Vladmir!5Anos-';
GRANT ALL PRIVILEGES ON NexlifyTTk.* TO 'gato'@'%';
FLUSH PRIVILEGES;

-- Etapa 3: Usar o banco de dados
USE NexlifyTTk;

-- Etapa 4: Limpeza e criação das tabelas (em ordem de dependência reversa)
DROP TABLE IF EXISTS LOG_ALTERACOES;
DROP TABLE IF EXISTS VEGETAIS;
DROP TABLE IF EXISTS TIPOS_VEGETAIS;
DROP TABLE IF EXISTS USUARIOS;
DROP TABLE IF EXISTS ESPECIE_GATOS;

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

-- Tabela de Tipos de Vegetais
CREATE TABLE TIPOS_VEGETAIS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Vegetais com Chave Estrangeira
CREATE TABLE VEGETAIS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100) NOT NULL,
    ID_TIPO INT,
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_VEGETAIS(ID)
        ON DELETE RESTRICT -- ALTERADO: Impede a exclusão de um tipo se estiver em uso
        ON UPDATE CASCADE
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

-- Inserções de dados (permanecem as mesmas)
-- ... (o restante do arquivo com os INSERTs não precisa ser alterado)