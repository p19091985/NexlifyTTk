-- Remove tabelas existentes para garantir um estado limpo ao reiniciar o banco
DROP TABLE IF EXISTS Usuarios;
DROP TABLE IF EXISTS LogSistemas;
DROP TABLE IF EXISTS LogEtapas;

-- Tabela de Usuários com níveis de acesso corporativos mais descritivos
CREATE TABLE Usuarios (
    LoginUsuario TEXT PRIMARY KEY NOT NULL,
    SenhaCriptografada TEXT NOT NULL,
    NomeCompleto TEXT NOT NULL,
    TipoAcesso TEXT NOT NULL CHECK (TipoAcesso IN (
        'Administrador Global',
        'Diretor de Operações',
        'Gerente de TI',
        'Supervisor de Produção',
        'Operador de Linha',
        'Analista de Dados',
        'Auditor Externo'
    ))
);

-- Inserindo usuários de exemplo com senhas JÁ CRIPTOGRAFADAS com bcrypt
-- As senhas originais são: admin, dir123, ti123, sup123, op123, ana123
INSERT INTO Usuarios (LoginUsuario, SenhaCriptografada, NomeCompleto, TipoAcesso) VALUES
('admin', '$2b$12$XwNof8boGFIgAm4alrGkAOaB/UxSZDuBl9NnIt7Y4zDL56qJkWU/O', 'Usuário Administrador', 'Administrador Global'),
('diretor.op', '$2b$12$HeEl0/HNy7aVOWiSQlv6q.MQno051lwo15pR9CPCOMaZTriNwznT2', 'Carlos Diretor', 'Diretor de Operações'),
('gerente.ti', '$2b$12$0hgHPcSz3nwWZiy/whOpGO.yehh15o/yyQ1rsHYXRGhxWFa8VXXNe', 'Beatriz Gerente', 'Gerente de TI'),
('supervisor.prod', '$2b$12$X2Y.0z4dFe2Y1lNPtvQug.L6q4s66Uj.C/dlvDBWHM8RCyirW2bpS', 'João Supervisor', 'Supervisor de Produção'),
('operador', '$2b$12$szK0ApZabmsw9uAUcRuok.4LAIW1.Et1q3OPAEp5h53LuEFuKiPAK', 'Maria Operadora', 'Operador de Linha'),
('analista.dados', '$2b$12$WZxQnpKG5dnLNLaS2QNQ2OKWaNaCeZU6GU.XVPIrbgEGlr9DPlQTy', 'Fernanda Analista', 'Analista de Dados');


CREATE TABLE tipos_linguagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

-- Dados iniciais para os tipos
INSERT INTO tipos_linguagem (nome) VALUES
('Estática'),
('Dinâmica'),
('Mista'),
('Funcional'),
('Lógica');


CREATE TABLE linguagens_programacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT,
    ano_criacao INTEGER,
    categoria TEXT
);

-- Dados de exemplo
INSERT INTO linguagens_programacao (nome, tipo, ano_criacao, categoria) VALUES
('C++', 'Estática', 1985, 'Linguagens Compiladas'),
('Java', 'Estática', 1995, 'Linguagens Compiladas'),
('Rust', 'Estática', 2010, 'Linguagens Compiladas'),
('Go', 'Estática', 2009, 'Linguagens Compiladas'),
('C#', 'Estática', 2000, 'Linguagens Compiladas'),
('Python', 'Dinâmica', 1991, 'Linguagens Interpretadas'),
('JavaScript', 'Dinâmica', 1995, 'Linguagens Interpretadas'),
('Ruby', 'Dinâmica', 1995, 'Linguagens Interpretadas'),
('PHP', 'Dinâmica', 1995, 'Linguagens Interpretadas');


CREATE TABLE log_alteracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    usuario TEXT NOT NULL,
    acao TEXT
);





