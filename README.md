## Nova Tela: Visualização de Pedidos

- **Nome da Tela:** Lista de Pedidos dos Clientes
- **Rota:** `/pedidos`
- **Tabelas Relacionadas:** `pedidos` e `clientes`
- **Consulta SQL Utilizada:**
  ```sql
  SELECT p.id_pedido, c.nome, c.cidade, c.estado,
         p.data_pedido, p.valor_total, p.status_pedido
  FROM pedidos p
  INNER JOIN clientes c ON c.id_cliente = p.id_cliente
  ORDER BY p.data_pedido DESC;
