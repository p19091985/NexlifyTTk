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

-- Etapa 2: Criar o login no servidor SQL
IF NOT EXISTS (SELECT * FROM sys.sql_logins WHERE name = 'gato')
BEGIN
    CREATE LOGIN gato WITH PASSWORD = '-Vladmir!5Anos-';
    PRINT 'Login "gato" criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Login "gato" já existe.';
END
GO

-- Etapa 3: Mudar para o contexto do novo banco de dados
USE NexlifyTTk;
GO

-- Etapa 4: Criar o usuário no banco de dados, associado ao login
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'gato')
BEGIN
    CREATE USER gato FOR LOGIN gato;
    PRINT 'Usuário "gato" criado no banco NexlifyTTk.';
END
ELSE
BEGIN
    PRINT 'Usuário "gato" já existe no banco NexlifyTTk.';
END
GO

-- Etapa 5: Conceder permissões de administrador ao usuário no banco
ALTER ROLE db_owner ADD MEMBER gato;
PRINT 'Permissões de db_owner concedidas ao usuário "gato".';
GO

-- Etapa 6: Limpeza e criação das tabelas
-- A ordem de DROP é inversa à da criação para respeitar as chaves estrangeiras
IF OBJECT_ID('dbo.LOG_ALTERACOES', 'U') IS NOT NULL DROP TABLE dbo.LOG_ALTERACOES;
IF OBJECT_ID('dbo.LINGUAGENS_PROGRAMACAO', 'U') IS NOT NULL DROP TABLE dbo.LINGUAGENS_PROGRAMACAO;
IF OBJECT_ID('dbo.ESPECIE_GATOS', 'U') IS NOT NULL DROP TABLE dbo.ESPECIE_GATOS;
IF OBJECT_ID('dbo.TIPOS_LINGUAGEM', 'U') IS NOT NULL DROP TABLE dbo.TIPOS_LINGUAGEM;
IF OBJECT_ID('dbo.USUARIOS', 'U') IS NOT NULL DROP TABLE dbo.USUARIOS;
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

-- Tabela de Tipos de Linguagem
CREATE TABLE TIPOS_LINGUAGEM (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME NVARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Linguagens com Chave Estrangeira
CREATE TABLE LINGUAGENS_PROGRAMACAO (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    NOME NVARCHAR(100) NOT NULL,
    ID_TIPO INT,
    ANO_CRIACAO INT,
    CATEGORIA NVARCHAR(100),
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_LINGUAGEM(ID) ON DELETE SET NULL ON UPDATE CASCADE
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
GO

PRINT 'Tabelas criadas e dados inseridos com sucesso em NexlifyTTk.';
GO