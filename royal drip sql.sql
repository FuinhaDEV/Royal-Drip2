/* ============================================================================
   PROJETO: Royal Drip (E-commerce de Moda / Streetwear)
   INTEGRANTES: [Isabelly Vitoria, Ana Beatriz Cristofolette, Leticia Cristina, Thiago Barbosa, Arthur de Jesus]
   DATA: 09/10/2026
   ----------------------------------------------------------------------------
   Usuários de teste (senhas já com hash do Werkzeug, o mesmo usado no Flask):
     lucas@email.com  / 123456     (Cliente)
     admin@email.com  / admin123   (Administrador)
   ============================================================================ */

-- ATENÇÃO: apaga o banco antigo e recria tudo do zero (evita conflito com as
-- tabelas da versão anterior: clientes, produtos com tamanho/cor, senhas inválidas...).
-- Se já tiver usuários cadastrados pelo site que quer manter, comente esta linha.
DROP DATABASE IF EXISTS ROYAL_DRIP_SQL;

CREATE DATABASE IF NOT EXISTS ROYAL_DRIP_SQL
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ROYAL_DRIP_SQL;

-- ----------------------------------------------------------------------------
-- 1. ESTRUTURA
-- ----------------------------------------------------------------------------

-- Perfis de acesso (Cliente / Administrador)
CREATE TABLE IF NOT EXISTS perfis (
    id_perfil INT AUTO_INCREMENT PRIMARY KEY,
    nome_perfil VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Os perfis precisam existir ANTES de qualquer usuário (chave estrangeira)
INSERT INTO perfis (id_perfil, nome_perfil) VALUES
(1, 'Cliente'),
(2, 'Administrador')
ON DUPLICATE KEY UPDATE nome_perfil = VALUES(nome_perfil);

-- Usuários (única tabela de login/cadastro; substitui "clientes")
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_perfil INT NOT NULL DEFAULT 1,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,          -- hash gerado por generate_password_hash
    telefone VARCHAR(20),
    cidade VARCHAR(50),
    estado CHAR(2),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_perfis FOREIGN KEY (id_perfil) REFERENCES perfis(id_perfil)
) ENGINE=InnoDB;

-- Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome_categoria VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Produtos (os mesmos 12 itens exibidos no site)
-- O tamanho NÃO fica aqui: um produto tem vários tamanhos, que são escolhidos
-- no carrinho / pedido.
CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nome_produto VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    estoque INT NOT NULL DEFAULT 0,
    imagem_url VARCHAR(255) DEFAULT 'default.jpg',
    ativo BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_produtos_categorias FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
) ENGINE=InnoDB;

-- Carrinho (um carrinho por usuário)
CREATE TABLE IF NOT EXISTS carrinho (
    id_carrinho INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_produto INT NOT NULL,
    tamanho VARCHAR(10) NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_carrinho_usuarios FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_carrinho_produtos FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
    -- mesmo produto + mesmo tamanho = mesma linha (soma a quantidade)
    CONSTRAINT uq_carrinho_item UNIQUE (id_usuario, id_produto, tamanho)
) ENGINE=InnoDB;

-- Pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(10,2) NOT NULL,
    status_pedido VARCHAR(30) DEFAULT 'Finalizado',
    CONSTRAINT fk_pedidos_usuarios FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- Itens do pedido
CREATE TABLE IF NOT EXISTS itens_pedido (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_produto INT NOT NULL,
    tamanho VARCHAR(10) NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_itens_pedidos FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    CONSTRAINT fk_itens_produtos FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
    CONSTRAINT uq_item_pedido UNIQUE (id_pedido, id_produto, tamanho)
) ENGINE=InnoDB;


-- ----------------------------------------------------------------------------
-- 2. DADOS DE TESTE
-- ----------------------------------------------------------------------------

-- Categorias
INSERT INTO categorias (id_categoria, nome_categoria) VALUES
(1, 'Camisetas'),
(2, 'Conjuntos'),
(3, 'Calças')
ON DUPLICATE KEY UPDATE nome_categoria = VALUES(nome_categoria);

-- Usuários (senhas com hash real do Werkzeug)
INSERT INTO usuarios (id, id_perfil, nome, email, senha, telefone, cidade, estado) VALUES
(1, 1, 'Lucas Silva',    'lucas@email.com',    'pbkdf2:sha256:1000000$mqA4pKyZJP1B6mRS$79ac46cec917c58cdb643e15645562bfbc8d80067d796507c86a5848c9f064f1', '11999990001', 'São Paulo',      'SP'),
(2, 1, 'Mariana Costa',  'mariana@email.com',  'pbkdf2:sha256:1000000$mqA4pKyZJP1B6mRS$79ac46cec917c58cdb643e15645562bfbc8d80067d796507c86a5848c9f064f1', '21999990002', 'Rio de Janeiro', 'RJ'),
(3, 1, 'Felipe Andrade', 'felipe@email.com',  'pbkdf2:sha256:1000000$mqA4pKyZJP1B6mRS$79ac46cec917c58cdb643e15645562bfbc8d80067d796507c86a5848c9f064f1', '41999990003', 'Curitiba',       'PR'),
(4, 1, 'Camila Rocha',   'camila@email.com',   'pbkdf2:sha256:1000000$mqA4pKyZJP1B6mRS$79ac46cec917c58cdb643e15645562bfbc8d80067d796507c86a5848c9f064f1', '31999990004', 'Belo Horizonte', 'MG'),
(5, 2, 'Administrador',  'admin@email.com',    'pbkdf2:sha256:1000000$BhqbB0S7ZbvI9OBE$27dbba1897d2df8f36ddfa48f0cef4fdbaf2f43722d1ceb4d14e5c945cdb5d41', '11999990005', 'São Paulo',      'SP')
ON DUPLICATE KEY UPDATE
    nome = VALUES(nome),
    id_perfil = VALUES(id_perfil),
    senha = VALUES(senha);   -- redefine a senha dos usuários de teste

-- Produtos: mesmos ids, nomes e preços do dicionário PRODUTOS do app.py
INSERT INTO produtos (id_produto, id_categoria, nome_produto, descricao, preco, estoque, imagem_url) VALUES
(1,  1, 'Camisa Boxy Dark Angel Drop 01',  'Modelagem ampla com corte streetwear moderno, algodão encorpado e acabamento premium.', 129.90, 45, 'imagens/camisas/camisa 1.jpg'),
(2,  1, 'Camisa Boxy Black Bite Drop 02',  'Corte oversized com visual urbano, estampa marcante e tecido confortável.',             139.90, 40, 'imagens/camisas/camisa 2.jpg'),
(3,  1, 'Camisa Boxy Light Bite Drop 03',  'Edição leve com visual clean, caimento amplo e acabamento premium.',                    149.90, 35, 'imagens/camisas/camisa 3.jpg'),
(4,  2, 'Conjunto Cinza Street Drop 01',   'Moletom pesado com capuz e calça cargo, ideal para clima frio.',                        289.90, 20, 'imagens/blusas_Conjuntos/conjunto moletom cinza.jpg'),
(5,  2, 'Conjunto UK Drop 02',             'Visual urbano com textura premium para um outfit monotonal.',                           299.90, 20, 'imagens/blusas_Conjuntos/USA.jpg'),
(6,  2, 'Conjunto Branco Street Drop 03',  'Estilo minimalista com acabamento refinado e tecido macio.',                            319.90, 18, 'imagens/blusas_Conjuntos/conjunto branco copy.jpg'),
(7,  2, 'Conjunto Blue Street Drop 04',    'Conjunto azul com visual esportivo e premium.',                                         329.90, 15, 'imagens/blusas_Conjuntos/conj2.jpg'),
(8,  2, 'Conjunto Camuflado Street Drop 05','Estampa camuflada com visual robusto e capuz reforçado.',                              339.90, 15, 'imagens/blusas_Conjuntos/conj3.jpg'),
(9,  2, 'Conjunto Cimento Street Drop 06', 'Tom cimento com acabamento refinado e caimento largo.',                                 349.90, 12, 'imagens/blusas_Conjuntos/conj4.jpg'),
(10, 3, 'Calça de Moletom Letringg Drop 07','Calça de moletom com conforto premium e modelagem moderna.',                           239.90, 25, 'imagens/calcas/Calça Moletom.jpg'),
(11, 3, 'Calça de Moletom Branca Drop 08', 'Visual clean e contemporâneo, com ajuste que favorece a modelagem ampla.',              247.90, 22, 'imagens/calcas/calça branca.jpg'),
(12, 3, 'Calça de Moletom Azul Drop 09',   'Visual esportivo, acabamento versátil e toque macio.',                                  249.90, 22, 'imagens/calcas/calça azul.jpg')
ON DUPLICATE KEY UPDATE
    nome_produto = VALUES(nome_produto),
    descricao    = VALUES(descricao),
    preco        = VALUES(preco),
    imagem_url   = VALUES(imagem_url);

-- Pedidos (valor_total = soma dos itens abaixo)
INSERT IGNORE INTO pedidos (id_pedido, id_usuario, data_pedido, valor_total, status_pedido) VALUES
(1001, 1, '2026-10-01 10:30:00', 269.80, 'Finalizado'),   -- 129.90 + 139.90
(1002, 2, '2026-10-02 14:15:00', 289.90, 'Finalizado'),   -- 289.90
(1003, 1, '2026-10-04 18:00:00', 569.80, 'Finalizado'),   -- 239.90 + 329.90
(1004, 3, '2026-10-05 11:20:00', 149.90, 'Finalizado');   -- 149.90

-- Itens dos pedidos
INSERT IGNORE INTO itens_pedido (id_pedido, id_produto, tamanho, quantidade, preco_unitario) VALUES
(1001, 1,  'G',  1, 129.90),
(1001, 2,  'M',  1, 139.90),
(1002, 4,  'GG', 1, 289.90),
(1003, 10, 'G',  1, 239.90),
(1003, 7,  'M',  1, 329.90),
(1004, 3,  'P',  1, 149.90);


-- ============================================================================
-- 3. RELATÓRIOS E TAREFAS ACADÊMICAS
-- ============================================================================

-- TAREFA 1: COUNT
SELECT COUNT(id_produto) AS quantidade_itens_catalogo FROM produtos;

-- TAREFA 2: SUM
SELECT SUM(preco * estoque) AS valor_total_estoque_reais FROM produtos;

-- TAREFA 3: AVG
SELECT AVG(preco) AS preco_medio_pecas_reais FROM produtos;

-- TAREFA 4: GROUP BY
SELECT id_categoria, COUNT(id_produto) AS total_produtos, AVG(preco) AS preco_medio_categoria_reais
FROM produtos
GROUP BY id_categoria;

-- TAREFA 5: INNER JOIN
SELECT c.nome_categoria, p.nome_produto, ip.quantidade, ip.preco_unitario AS preco_unitario_reais
FROM produtos p
INNER JOIN categorias c ON p.id_categoria = c.id_categoria
INNER JOIN itens_pedido ip ON p.id_produto = ip.id_produto;

-- DESAFIO: INNER JOIN + GROUP BY
SELECT c.nome_categoria,
       SUM(ip.quantidade) AS total_pecas_vendidas,
       SUM(ip.quantidade * ip.preco_unitario) AS faturamento_categoria_reais
FROM categorias c
INNER JOIN produtos p ON c.id_categoria = p.id_categoria
INNER JOIN itens_pedido ip ON p.id_produto = ip.id_produto
GROUP BY c.id_categoria, c.nome_categoria;


-- ============================================================================
-- 4. CONSULTAS ADICIONAIS (COUNT, SUM, AVG, GROUP BY, INNER JOIN)
-- ============================================================================

-- CONSULTA 1: COUNT + INNER JOIN + GROUP BY
-- Quantidade de pedidos por cliente
SELECT u.nome AS cliente,
       COUNT(p.id_pedido) AS total_pedidos
FROM usuarios u
INNER JOIN pedidos p ON u.id = p.id_usuario
GROUP BY u.id, u.nome
ORDER BY total_pedidos DESC, u.nome;

-- CONSULTA 2: SUM + INNER JOIN + GROUP BY
-- Peças vendidas e faturamento por categoria
SELECT c.nome_categoria AS categoria,
       SUM(ip.quantidade) AS pecas_vendidas,
       SUM(ip.quantidade * ip.preco_unitario) AS faturamento_reais
FROM categorias c
INNER JOIN produtos p      ON c.id_categoria = p.id_categoria
INNER JOIN itens_pedido ip ON p.id_produto = ip.id_produto
GROUP BY c.id_categoria, c.nome_categoria
ORDER BY faturamento_reais DESC;

-- CONSULTA 3: AVG + INNER JOIN + GROUP BY
-- Ticket médio (valor médio dos pedidos) por cliente
SELECT u.nome AS cliente,
       ROUND(AVG(p.valor_total), 2) AS ticket_medio_reais
FROM usuarios u
INNER JOIN pedidos p ON u.id = p.id_usuario
GROUP BY u.id, u.nome
ORDER BY ticket_medio_reais DESC;

-- CONSULTA 4: COUNT + AVG + SUM + GROUP BY
-- Resumo do catálogo por categoria (qtd. de produtos, preço médio e estoque)
SELECT c.nome_categoria AS categoria,
       COUNT(p.id_produto) AS qtd_produtos,
       ROUND(AVG(p.preco), 2) AS preco_medio_reais,
       SUM(p.estoque) AS pecas_em_estoque
FROM categorias c
INNER JOIN produtos p ON c.id_categoria = p.id_categoria
GROUP BY c.id_categoria, c.nome_categoria
ORDER BY c.nome_categoria;

-- CONSULTA 5: SUM + COUNT + INNER JOIN + GROUP BY
-- Pedidos e faturamento por estado do cliente
SELECT u.estado,
       COUNT(p.id_pedido) AS total_pedidos,
       SUM(p.valor_total) AS faturamento_reais
FROM usuarios u
INNER JOIN pedidos p ON u.id = p.id_usuario
GROUP BY u.estado
ORDER BY faturamento_reais DESC;

-- CONSULTA DA TELA DE PEDIDOS DOS CLIENTES
SELECT 
    p.id_pedido,
    p.data_pedido,
    p.valor_total,
    p.status_pedido AS status,
    u.nome AS cliente_nome,
    u.email AS cliente_email
FROM pedidos p
INNER JOIN usuarios u ON p.id_usuario = u.id
ORDER BY p.data_pedido DESC;

-- VERIFICAR A ESTRUTURA DA TABELA PEDIDOS
DESCRIBE pedidos;