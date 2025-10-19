-- Etapa 1: Criar o banco de dados se ele não existir (usando minúsculas)
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'nexlifyttk')
BEGIN
    CREATE DATABASE nexlifyttk;
    PRINT 'Banco de dados nexlifyttk criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Banco de dados nexlifyttk já existe.';
END
GO

-- Mudar para o contexto do banco de dados (usando minúsculas)
USE nexlifyttk;
GO

-- ... (Comandos de criação de login/usuário SQL Server, se houver, precisam ser adaptados aqui) ...
-- Exemplo genérico (ajuste conforme sua configuração):
-- IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'gato')
-- BEGIN
--     CREATE LOGIN gato WITH PASSWORD = '-Vladmir!5Anos-';
--     PRINT 'Login gato criado.';
-- END
-- GO
-- IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'gato')
-- BEGIN
--     CREATE USER gato FOR LOGIN gato;
--     PRINT 'Usuário gato criado no banco nexlifyttk.';
--     ALTER ROLE db_owner ADD MEMBER gato; -- Concede permissões amplas, ajuste se necessário
--     PRINT 'Permissões concedidas ao usuário gato.';
-- END
-- GO


-- Etapa 6: Limpeza e criação das tabelas (usando minúsculas)
-- A ordem de DROP é inversa à da criação para respeitar as chaves estrangeiras
IF OBJECT_ID('dbo.log_alteracoes', 'U') IS NOT NULL DROP TABLE dbo.log_alteracoes;
IF OBJECT_ID('dbo.vegetais', 'U') IS NOT NULL DROP TABLE dbo.vegetais;
IF OBJECT_ID('dbo.tipos_vegetais', 'U') IS NOT NULL DROP TABLE dbo.tipos_vegetais;
IF OBJECT_ID('dbo.usuarios', 'U') IS NOT NULL DROP TABLE dbo.usuarios;
IF OBJECT_ID('dbo.especie_gatos', 'U') IS NOT NULL DROP TABLE dbo.especie_gatos;
GO

-- Tabela de Usuários (minúsculas)
CREATE TABLE usuarios (
    login_usuario NVARCHAR(255) PRIMARY KEY NOT NULL,
    senha_criptografada NVARCHAR(255) NOT NULL,
    nome_completo NVARCHAR(255) NOT NULL,
    tipo_acesso NVARCHAR(100) NOT NULL CHECK (tipo_acesso IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);

-- Tabela de Tipos de Vegetais (minúsculas)
CREATE TABLE tipos_vegetais (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Vegetais com Chave Estrangeira (minúsculas)
CREATE TABLE vegetais (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL,
    id_tipo INT,
    FOREIGN KEY (id_tipo) REFERENCES tipos_vegetais(id) ON DELETE NO ACTION ON UPDATE CASCADE
);

-- Tabela de Log de Alterações (minúsculas)
CREATE TABLE log_alteracoes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    -- CORREÇÃO: Nome da coluna timestamp em minúsculas
    timestamp DATETIME2 NOT NULL,
    login_usuario NVARCHAR(255),
    acao NVARCHAR(MAX),
    FOREIGN KEY (login_usuario) REFERENCES usuarios(login_usuario) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela Especie Gatos (minúsculas)
CREATE TABLE especie_gatos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome_especie NVARCHAR(255) NOT NULL UNIQUE,
    pais_origem NVARCHAR(255),
    temperamento NVARCHAR(255)
);
GO

-- Inserções de dados (usando nomes de tabela/coluna minúsculos)
INSERT INTO usuarios (login_usuario, senha_criptografada, nome_completo, tipo_acesso) VALUES
('admin', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Usuário Administrador', 'Administrador Global'),
('dev_user', '$2b$12$TgcQ51usbRmBjfGtris6eueXiKMbJpfSpsFpuyM4QE/qwqmcEX9By', 'Usuário de Desenvolvimento', 'Administrador Global'),
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

INSERT INTO tipos_vegetais (nome) VALUES ('Raízes e Tubérculos'), ('Folhas'), ('Flores e Inflorescências'), ('Frutos'), ('Legumes');

INSERT INTO vegetais (nome, id_tipo) VALUES
('Abóbora', 4), ('Abobrinha', 4), ('Agrião', 2), ('Aipim', 1), ('Alface', 2), ('Alho', 1), ('Almeirão', 2),
('Batata-doce', 1), ('Batata', 1), ('Berinjela', 4), ('Beterraba', 1), ('Brócolis', 3), ('Cebola', 1),
('Cenoura', 1), ('Chuchu', 4), ('Coentro', 2), ('Couve', 2), ('Couve-flor', 3), ('Ervilha', 5), ('Espinafre', 2),
('Feijão-vagem', 5), ('Inhame', 1), ('Jiló', 4), ('Maxixe', 4), ('Milho', 4), ('Pepino', 4), ('Pimentão', 4),
('Quiabo', 4), ('Rabanete', 1), ('Repolho', 2);

INSERT INTO especie_gatos (nome_especie, pais_origem, temperamento) VALUES
('Siamês', 'Tailândia', 'Inteligente e Afetuoso'),
('Persa', 'Irã (Pérsia)', 'Calmo e Dócil'),
('Maine Coon', 'Estados Unidos', 'Gentil e Brincalhão'),
('Bengal', 'Estados Unidos', 'Ativo e Curioso');
GO

PRINT 'Tabelas criadas e dados inseridos com sucesso em nexlifyttk.';
GO