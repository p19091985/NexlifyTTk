-- Etapa 1: Criar o banco de dados se ele não existir
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'NexlifyTTk')
BEGIN
    CREATE DATABASE NexlifyTTk;
    PRINT 'Banco de dados NexlifyTTk criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Banco de dados NexlifyTTk já existe.';
END
GO

-- ... (comandos de criação de login e usuário mantidos) ...
USE NexlifyTTk;
GO
-- ... (comandos de criação de login e usuário mantidos) ...
GO

-- Etapa 6: Limpeza e criação das tabelas
-- A ordem de DROP é inversa à da criação para respeitar as chaves estrangeiras
IF OBJECT_ID('dbo.LOG_ALTERACOES', 'U') IS NOT NULL DROP TABLE dbo.LOG_ALTERACOES;
IF OBJECT_ID('dbo.VEGETAIS', 'U') IS NOT NULL DROP TABLE dbo.VEGETAIS;
IF OBJECT_ID('dbo.TIPOS_VEGETAIS', 'U') IS NOT NULL DROP TABLE dbo.TIPOS_VEGETAIS;
IF OBJECT_ID('dbo.USUARIOS', 'U') IS NOT NULL DROP TABLE dbo.USUARIOS;
IF OBJECT_ID('dbo.ESPECIE_GATOS', 'U') IS NOT NULL DROP TABLE dbo.ESPECIE_GATOS;
GO

-- Tabela de Usuários
CREATE TABLE USUARIOS (
    LOGIN_USUARIO NVARCHAR(255) PRIMARY KEY NOT NULL,
    SENHA_CRIPTOGRAFADA NVARCHAR(255) NOT NULL,
    NOME_COMPLETO NVARCHAR(255) NOT NULL,
    TIPO_ACESSO NVARCHAR(100) NOT NULL CHECK (TIPO_ACESSO IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);

-- Tabela de Tipos de Vegetais
CREATE TABLE TIPOS_VEGETAIS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME NVARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Vegetais com Chave Estrangeira
CREATE TABLE VEGETAIS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME NVARCHAR(100) NOT NULL,
    ID_TIPO INT,
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_VEGETAIS(ID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela de Log de Alterações
CREATE TABLE LOG_ALTERACOES (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    TIMESTAMP DATETIME2 NOT NULL,
    LOGIN_USUARIO NVARCHAR(255),
    ACAO NVARCHAR(MAX),
    FOREIGN KEY (LOGIN_USUARIO) REFERENCES USUARIOS(LOGIN_USUARIO) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela Especie Gatos
CREATE TABLE ESPECIE_GATOS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME_ESPECIE NVARCHAR(255) NOT NULL UNIQUE,
    PAIS_ORIGEM NVARCHAR(255),
    TEMPERAMENTO NVARCHAR(255)
);
GO

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
(-- Etapa 1: Criar o banco de dados se ele não existir
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'NexlifyTTk')
BEGIN
    CREATE DATABASE NexlifyTTk;
    PRINT 'Banco de dados NexlifyTTk criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Banco de dados NexlifyTTk já existe.';
END
GO

USE NexlifyTTk;
GO

-- Etapa 6: Limpeza e criação das tabelas
IF OBJECT_ID('dbo.LOG_ALTERACOES', 'U') IS NOT NULL DROP TABLE dbo.LOG_ALTERACOES;
IF OBJECT_ID('dbo.VEGETAIS', 'U') IS NOT NULL DROP TABLE dbo.VEGETAIS;
IF OBJECT_ID('dbo.TIPOS_VEGETAIS', 'U') IS NOT NULL DROP TABLE dbo.TIPOS_VEGETAIS;
IF OBJECT_ID('dbo.USUARIOS', 'U') IS NOT NULL DROP TABLE dbo.USUARIOS;
IF OBJECT_ID('dbo.ESPECIE_GATOS', 'U') IS NOT NULL DROP TABLE dbo.ESPECIE_GATOS;
GO

-- Tabela de Usuários
CREATE TABLE USUARIOS (
    LOGIN_USUARIO NVARCHAR(255) PRIMARY KEY NOT NULL,
    SENHA_CRIPTOGRAFADA NVARCHAR(255) NOT NULL,
    NOME_COMPLETO NVARCHAR(255) NOT NULL,
    TIPO_ACESSO NVARCHAR(100) NOT NULL CHECK (TIPO_ACESSO IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);

-- Tabela de Tipos de Vegetais
CREATE TABLE TIPOS_VEGETAIS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME NVARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Vegetais com Chave Estrangeira
CREATE TABLE VEGETAIS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME NVARCHAR(100) NOT NULL,
    ID_TIPO INT,
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_VEGETAIS(ID) ON DELETE NO ACTION ON UPDATE CASCADE
);

-- Tabela de Log de Alterações
CREATE TABLE LOG_ALTERACOES (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    TIMESTAMP DATETIME2 NOT NULL,
    LOGIN_USUARIO NVARCHAR(255),
    ACAO NVARCHAR(MAX),
    FOREIGN KEY (LOGIN_USUARIO) REFERENCES USUARIOS(LOGIN_USUARIO) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela Especie Gatos
CREATE TABLE ESPECIE_GATOS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME_ESPECIE NVARCHAR(255) NOT NULL UNIQUE,
    PAIS_ORIGEM NVARCHAR(255),
    TEMPERAMENTO NVARCHAR(255)
);
GO

-- Dados de inserção (o restante do arquivo permanece o mesmo)
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
GO

PRINT 'Tabelas criadas e dados inseridos com sucesso em NexlifyTTk.';
GO'Bengal', 'Estados Unidos', 'Ativo e Curioso');
GO

PRINT 'Tabelas criadas e dados inseridos com sucesso em NexlifyTTk.';
GO