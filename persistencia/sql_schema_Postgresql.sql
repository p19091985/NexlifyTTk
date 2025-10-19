SELECT
    pg_terminate_backend(pg_stat_activity.pid)
FROM
    pg_stat_activity
WHERE
    pg_stat_activity.datname = 'nexlifyttk' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS nexlifyttk;
DROP ROLE IF EXISTS gato;
CREATE ROLE gato LOGIN PASSWORD '-Vladmir!5Anos-';
CREATE DATABASE nexlifyttk
    WITH
    OWNER = gato
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;
GRANT CONNECT ON DATABASE nexlifyttk TO gato;
GRANT CREATE ON SCHEMA public TO gato;
DROP TABLE IF EXISTS log_alteracoes;
DROP TABLE IF EXISTS vegetais;
DROP TABLE IF EXISTS tipos_vegetais;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS especie_gatos;
CREATE TABLE usuarios (
    login_usuario VARCHAR(255) PRIMARY KEY NOT NULL,
    senha_criptografada VARCHAR(255) NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    tipo_acesso VARCHAR(100) NOT NULL CHECK (tipo_acesso IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);
CREATE TABLE tipos_vegetais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE vegetais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_tipo INT,
    FOREIGN KEY (id_tipo) REFERENCES tipos_vegetais(id) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE TABLE log_alteracoes (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    login_usuario VARCHAR(255),
    acao TEXT,
    FOREIGN KEY (login_usuario) REFERENCES usuarios(login_usuario) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE TABLE especie_gatos (
    id SERIAL PRIMARY KEY,
    nome_especie VARCHAR(255) NOT NULL UNIQUE,
    pais_origem VARCHAR(255),
    temperamento VARCHAR(255)
);
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gato;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gato;
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
INSERT INTO tipos_vegetais (nome) VALUES
('Raízes e Tubérculos'), ('Folhas'), ('Flores e Inflorescências'), ('Frutos'), ('Legumes');
INSERT INTO vegetais (nome, id_tipo) VALUES
('Abóbora', 4), ('Abobrinha', 4), ('Agrião', 2), ('Aipim', 1), ('Alface', 2), ('Alho', 1), ('Almeirão', 2),
('Batata-doce', 1), ('Batata', 1), ('Berinjela', 4), ('Beterraba', 1), ('Brócolis', 3), ('Cebola', 1); 
INSERT INTO especie_gatos (nome_especie, pais_origem, temperamento) VALUES
('Siamês', 'Tailândia', 'Inteligente e Afetuoso'),
('Persa', 'Irã (Pérsia)', 'Calmo e Dócil'),
('Maine Coon', 'Estados Unidos', 'Gentil e Brincalhão'),
('Bengal', 'Estados Unidos', 'Ativo e Curioso');