-- MariaDB é altamente compatível com MySQL.
-- Este script cria o banco, o usuário e as tabelas para o ambiente MariaDB/MySQL.

-- Etapa 1: Criar o banco de dados se ele não existir (usando minúsculas)
CREATE DATABASE IF NOT EXISTS nexlifyttk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Etapa 2: Conceder permissões ao root para conexões remotas (MANTER COMO ESTÁ, se necessário)
-- GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '-Vladmir!5Anos-' WITH GRANT OPTION;
-- FLUSH PRIVILEGES;

-- Etapa 3: Criar o usuário 'gato' e conceder permissões no banco nexlifyttk (usando minúsculas)
CREATE USER IF NOT EXISTS 'gato'@'%' IDENTIFIED BY '-Vladmir!5Anos-';
GRANT ALL PRIVILEGES ON nexlifyttk.* TO 'gato'@'%' IDENTIFIED BY '-Vladmir!5Anos-';
FLUSH PRIVILEGES;

-- Etapa 4: Usar o banco de dados (usando minúsculas)
USE nexlifyttk;

-- Etapa 5: Limpeza das tabelas (em ordem de dependência reversa, usando minúsculas)
DROP TABLE IF EXISTS log_alteracoes;
DROP TABLE IF EXISTS vegetais;
DROP TABLE IF EXISTS tipos_vegetais;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS especie_gatos;

-- Tabela de Usuários (minúsculas)
CREATE TABLE usuarios (
    login_usuario VARCHAR(255) PRIMARY KEY NOT NULL,
    senha_criptografada VARCHAR(255) NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    tipo_acesso VARCHAR(100) NOT NULL CHECK (tipo_acesso IN (
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo'
    ))
);

-- Tabela de Tipos de Vegetais (minúsculas)
CREATE TABLE tipos_vegetais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Vegetais com Chave Estrangeira (minúsculas)
CREATE TABLE vegetais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_tipo INT,
    FOREIGN KEY (id_tipo) REFERENCES tipos_vegetais(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela de Log de Alterações (minúsculas)
CREATE TABLE log_alteracoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    login_usuario VARCHAR(255),
    acao TEXT,
    FOREIGN KEY (login_usuario) REFERENCES usuarios(login_usuario) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela Especie Gatos (minúsculas)
CREATE TABLE especie_gatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_especie VARCHAR(255) NOT NULL UNIQUE,
    pais_origem VARCHAR(255),
    temperamento VARCHAR(255)
);

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

INSERT INTO tipos_vegetais (nome) VALUES
('Raízes e Tubérculos'), ('Folhas'), ('Flores e Inflorescências'), ('Frutos'), ('Legumes');

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