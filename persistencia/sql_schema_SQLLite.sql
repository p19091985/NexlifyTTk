-- Remove tabelas existentes para garantir um estado limpo, respeitando a ordem das dependências
DROP TABLE IF EXISTS LOG_ALTERACOES;
DROP TABLE IF EXISTS VEGETAIS;
DROP TABLE IF EXISTS TIPOS_VEGETAIS;
DROP TABLE IF EXISTS USUARIOS;
DROP TABLE IF EXISTS ESPECIE_GATOS;

-- Tabela de Usuários
CREATE TABLE USUARIOS (
    LOGIN_USUARIO TEXT PRIMARY KEY NOT NULL,
    SENHA_CRIPTOGRAFADA TEXT NOT NULL,
    NOME_COMPLETO TEXT NOT NULL,
    TIPO_ACESSO TEXT NOT NULL CHECK (TIPO_ACESSO IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
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

-- Tabela de Tipos de Vegetais
CREATE TABLE TIPOS_VEGETAIS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NOME TEXT NOT NULL UNIQUE
);
INSERT INTO TIPOS_VEGETAIS (NOME) VALUES ('Raízes e Tubérculos');
INSERT INTO TIPOS_VEGETAIS (NOME) VALUES ('Folhas');
INSERT INTO TIPOS_VEGETAIS (NOME) VALUES ('Flores e Inflorescências');
INSERT INTO TIPOS_VEGETAIS (NOME) VALUES ('Frutos');
INSERT INTO TIPOS_VEGETAIS (NOME) VALUES ('Legumes');

-- Tabela de Vegetais com Chave Estrangeira
CREATE TABLE VEGETAIS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NOME TEXT NOT NULL,
    ID_TIPO INTEGER,
    FOREIGN KEY (ID_TIPO) REFERENCES TIPOS_VEGETAIS (ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Abóbora', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Abobrinha', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Agrião', 2);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Aipim', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Alface', 2);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Alho', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Almeirão', 2);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Batata-doce', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Batata', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Berinjela', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Beterraba', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Brócolis', 3);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Cebola', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Cenoura', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Chuchu', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Coentro', 2);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Couve', 2);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Couve-flor', 3);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Ervilha', 5);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Espinafre', 2);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Feijão-vagem', 5);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Inhame', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Jiló', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Maxixe', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Milho', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Pepino', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Pimentão', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Quiabo', 4);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Rabanete', 1);
INSERT INTO VEGETAIS (NOME, ID_TIPO) VALUES ('Repolho', 2);

-- Tabela de Log de Alterações
CREATE TABLE LOG_ALTERACOES (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TIMESTAMP DATETIME NOT NULL,
    LOGIN_USUARIO TEXT,
    ACAO TEXT,
    FOREIGN KEY (LOGIN_USUARIO) REFERENCES USUARIOS (LOGIN_USUARIO)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Tabela para a demonstração de CRUD
CREATE TABLE ESPECIE_GATOS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NOME_ESPECIE TEXT NOT NULL UNIQUE,
    PAIS_ORIGEM TEXT,
    TEMPERAMENTO TEXT
);

INSERT INTO ESPECIE_GATOS (NOME_ESPECIE, PAIS_ORIGEM, TEMPERAMENTO) VALUES
('Siamês', 'Tailândia', 'Inteligente e Afetuoso'),
('Persa', 'Irã (Pérsia)', 'Calmo e Dócil'),
('Maine Coon', 'Estados Unidos', 'Gentil e Brincalhão'),
('Bengal', 'Estados Unidos', 'Ativo e Curioso');