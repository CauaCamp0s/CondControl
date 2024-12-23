# CondControl
CondControl is a management system designed to help condominium managers organize and manage day-to-day activities and operations efficiently. It offers a series of functionalities that allow integrated control of various areas, such as resident management, finances, services and security.


create database condominio_db;
use condominio_db;

-- Criando a tabela de Categorias (primeiro, pois é referenciada por receitas)
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
);

-- Agora crie a tabela de Receitas (depois da tabela de categorias)
CREATE TABLE receitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    data DATE NOT NULL,
    categoria_id INT NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
);

-- Continuar com o restante das tabelas...

-- Criando a tabela de Moradores
CREATE TABLE moradores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    moradia VARCHAR(50) NOT NULL,
    apartamento VARCHAR(10) NOT NULL,
    senha VARCHAR(255) NOT NULL
);

-- Criando a tabela de Finanças
CREATE TABLE financas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('Receita', 'Despesa') NOT NULL,
    descricao VARCHAR(255),
    valor DECIMAL(10, 2) NOT NULL,
    data DATE NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    morador_id INT,
    FOREIGN KEY (morador_id) REFERENCES moradores(id) ON DELETE SET NULL
);

-- Criando a tabela de Áreas Comuns
CREATE TABLE areas_comuns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    capacidade INT,
    disponivel BOOLEAN DEFAULT TRUE,
    quantidade INT NOT NULL,
    imagem VARCHAR(255) NOT NULL
);

-- Criando a tabela de Reservas
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area_id INT NOT NULL,
    morador_id INT NOT NULL,
    data_reserva DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    status ENUM('Pendente', 'Confirmada', 'Cancelada') DEFAULT 'Pendente',
    FOREIGN KEY (area_id) REFERENCES areas_comuns(id) ON DELETE CASCADE,
    FOREIGN KEY (morador_id) REFERENCES moradores(id) ON DELETE CASCADE
);

-- Criando a tabela de Comunicados
CREATE TABLE comunicados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    morador_id INT,
    FOREIGN KEY (morador_id) REFERENCES moradores(id) ON DELETE SET NULL
);

-- Criando a tabela de Ocorrências
CREATE TABLE ocorrencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    morador_id INT NOT NULL,
    tipo ENUM('Reclamação', 'Incidente', 'Sugestão') NOT NULL,
    descricao TEXT NOT NULL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Aberta', 'Em andamento', 'Resolvida') DEFAULT 'Aberta',
    FOREIGN KEY (morador_id) REFERENCES moradores(id) ON DELETE CASCADE
);

-- Criando a tabela de Visitantes
CREATE TABLE visitantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR(50),
    morador_id INT NOT NULL,
    data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_saida DATETIME,
    FOREIGN KEY (morador_id) REFERENCES moradores(id) ON DELETE CASCADE
);

-- Criando a tabela de Taxas de Condomínio
CREATE TABLE taxas_condominio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    condominio_id INT NOT NULL,
    valor FLOAT NOT NULL,
    data_vencimento DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pendente'
);

-- Criando a tabela de Manutenções
CREATE TABLE manutencao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL,
    data_programada DATE NOT NULL,
    custo_estimado FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'programada'
);

-- Criando a tabela de Despesas
CREATE TABLE despesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    data DATE NOT NULL,
    categoria VARCHAR(100) NOT NULL
);




INSERT INTO categorias (nome) VALUES 
('Manutenção'),
('Limpeza'),
('Segurança'),
('Administração');


INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES 
('Aluguel de salão de festas', 500.00, '2024-09-01', 1),
('Contribuição extra', 300.00, '2024-09-05', 2),
('Multa por atraso', 150.00, '2024-09-10', 3);


INSERT INTO moradores (nome, email, telefone, moradia, apartamento, senha) VALUES 
('João Silva', 'joao.silva@gmail.com', '999999999', 'Bloco A', '101', 'senha123'),
('Maria Souza', 'maria.souza@hotmail.com', '988888888', 'Bloco B', '202', 'senha456'),
('Carlos Almeida', 'carlos.almeida@yahoo.com', '977777777', 'Bloco C', '303', 'senha789');


INSERT INTO financas (tipo, descricao, valor, data, categoria, morador_id) VALUES 
('Receita', 'Contribuição de morador', 250.00, '2024-09-01', 'Contribuição', 1),
('Despesa', 'Reparos na piscina', 1200.00, '2024-09-15', 'Manutenção', NULL),
('Receita', 'Taxa de condomínio', 350.00, '2024-09-05', 'Taxa', 2);



INSERT INTO areas_comuns (nome, descricao, capacidade, quantidade, imagem) VALUES 
('Salão de Festas', 'Salão para eventos e festas', 50, 1, 'salao.jpg'),
('Piscina', 'Piscina para uso dos moradores', 30, 1, 'piscina.jpg'),
('Quadra Poliesportiva', 'Espaço para esportes diversos', 20, 1, 'quadra.jpg');


INSERT INTO visitantes (nome, documento, morador_id) VALUES 
('Lucas Pereira', '123456789', 1),
('Ana Santos', '987654321', 2),
('Marcos Lima', '456789123', 3);



INSERT INTO ocorrencias (morador_id, tipo, descricao) VALUES 
(1, 'Reclamação', 'Barulho excessivo após as 22h no Bloco B.'),
(2, 'Incidente', 'Vazamento no cano do apartamento 202.'),
(3, 'Sugestão', 'Instalação de mais lixeiras nas áreas comuns.');


INSERT INTO taxas_condominio (condominio_id, valor, data_vencimento, status) VALUES 
(1, 300.00, '2024-10-05', 'pendente'),
(1, 300.00, '2024-11-05', 'pendente');


INSERT INTO manutencao (descricao, data_programada, custo_estimado, status) VALUES 
('Troca do portão principal', '2024-10-10', 1500.00, 'programada'),
('Reparos na quadra', '2024-11-15', 800.00, 'programada');


INSERT INTO despesas (descricao, valor, data, categoria) VALUES 
('Compra de materiais de limpeza', 300.00, '2024-09-10', 'Limpeza'),
('Conserto da cerca elétrica', 750.00, '2024-09-12', 'Segurança');


INSERT INTO comunicados (titulo, mensagem, morador_id) VALUES 
('Manutenção do Elevador', 'O elevador do Bloco A estará fora de serviço no dia 15/10 para manutenção.', 1),
('Limpeza da Piscina', 'A piscina será limpa no dia 20/10. Por favor, evitem o uso nesse dia.', 2),
('Reunião de Condôminos', 'Convocamos todos os condôminos para uma reunião no dia 25/10 às 19h no salão de festas.', 3),
('Troca de Segurança', 'A partir do dia 01/11, a empresa de segurança do condomínio será trocada. A nova empresa será a XYZ.', 1),
('Feira de Artesanato', 'No dia 30/10, haverá uma ra de artesanato na área comum. Todos estão convidados!', 2),
('Mudança de Horário da Piscina', 'A partir do dia 05/11, o horário de funcionamento da piscina será das 8h às 20h.', 3),fei
('Atualização sobre o Wi-Fi', 'O serviço de Wi-Fi nas áreas comuns será restabelecido até o dia 10/11.', 1),
('Festa de Natal do Condomínio', 'A festa de Natal do condomínio acontecerá no dia 15/12. Mais detalhes serão enviados posteriormente.', 2);


#   C o n d C o n t r o l  
 