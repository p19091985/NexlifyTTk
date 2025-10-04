-- Remove tabelas existentes para garantir um estado limpo, respeitando a ordem das dependências
DROP TABLE IF EXISTS log_alteracoes;
DROP TABLE IF EXISTS linguagens_programacao;
DROP TABLE IF EXISTS tipos_linguagem;
DROP TABLE IF EXISTS Usuarios;

-- Tabela de Usuários (sem alterações, é a tabela "pai")
CREATE TABLE Usuarios (
    LoginUsuario TEXT PRIMARY KEY NOT NULL,
    SenhaCriptografada TEXT NOT NULL,
    NomeCompleto TEXT NOT NULL,
    TipoAcesso TEXT NOT NULL CHECK (TipoAcesso IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);

INSERT INTO Usuarios (LoginUsuario, SenhaCriptografada, NomeCompleto, TipoAcesso) VALUES
('admin', '$2b$12$XwNof8boGFIgAm4alrGkAOaB/UxSZDuBl9NnIt7Y4zDL56qJkWU/O', 'Usuário Administrador', 'Administrador Global'),
('diretor.op', '$2b$12$HeEl0/HNy7aVOWiSQlv6q.MQno051lwo15pR9CPCOMaZTriNwznT2', 'Carlos Diretor', 'Diretor de Operações'),
('gerente.ti', '$2b$12$0hgHPcSz3nwWZiy/whOpGO.yehh15o/yyQ1rsHYXRGhxWFa8VXXNe', 'Beatriz Gerente', 'Gerente de TI');

-- Tabela de Tipos de Linguagem (sem alterações, é a tabela "pai")
CREATE TABLE tipos_linguagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

INSERT INTO tipos_linguagem (nome) VALUES ('Estática'), ('Dinâmica'), ('Mista'), ('Funcional'), ('Lógica');


-- Tabela de Linguagens com Chave Estrangeira
CREATE TABLE linguagens_programacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    id_tipo INTEGER, -- Coluna para a chave estrangeira
    ano_criacao INTEGER,
    categoria TEXT,
    -- Definição da Relação de Cardinalidade
    FOREIGN KEY (id_tipo) REFERENCES tipos_linguagem (id)
        ON DELETE SET NULL -- Se um tipo for apagado, o campo na linguagem fica nulo
        ON UPDATE CASCADE   -- Se o id de um tipo mudar, atualiza aqui também
);

-- Inserindo dados usando o ID do tipo correspondente
INSERT INTO linguagens_programacao (nome, id_tipo, ano_criacao, categoria) VALUES
('C++', 1, 1985, 'Linguagens Compiladas'),  -- 1 = Estática
('Java', 1, 1995, 'Linguagens Compiladas'), -- 1 = Estática
('Rust', 1, 2010, 'Linguagens Compiladas'), -- 1 = Estática
('Python', 2, 1991, 'Linguagens Interpretadas'), -- 2 = Dinâmica
('JavaScript', 2, 1995, 'Linguagens Interpretadas');


-- Tabela de Log de Alterações com Chave Estrangeira
CREATE TABLE log_alteracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    login_usuario TEXT, -- Coluna para a chave estrangeira
    acao TEXT,
    -- Definição da Relação de Cardinalidade
    FOREIGN KEY (login_usuario) REFERENCES Usuarios (LoginUsuario)
        ON DELETE SET NULL -- Se um usuário for apagado, o log não é perdido, apenas desassociado
        ON UPDATE CASCADE   -- Se o login de um usuário mudar, o log é atualizado
);


-- Adicione estas linhas ao final do seu arquivo sql_schema.sql

-- Tabela para a nova demonstração de CRUD
CREATE TABLE especie_gatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_especie TEXT NOT NULL UNIQUE,
    pais_origem TEXT,
    temperamento TEXT
);

-- Inserindo alguns dados de exemplo
INSERT INTO especie_gatos (nome_especie, pais_origem, temperamento) VALUES
('Siamês', 'Tailândia', 'Inteligente e Afetuoso'),
('Persa', 'Irã (Pérsia)', 'Calmo e Dócil'),
('Maine Coon', 'Estados Unidos', 'Gentil e Brincalhão'),
('Bengal', 'Estados Unidos', 'Ativo e Curioso');