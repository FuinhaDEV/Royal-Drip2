document.addEventListener("DOMContentLoaded", function () {
  const botoesFiltro = document.querySelectorAll(".btn-filtro");
  const produtos = document.querySelectorAll(".produto-card");

  botoesFiltro.forEach((botao) => {
    botao.addEventListener("click", function (e) {
      e.preventDefault();

      // 1. Destaque visual do botão selecionado
      botoesFiltro.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      // 2. Categoria escolhida
      const categoriaEscolhida = this.getAttribute("data-filter");

      // 3. Filtrar produtos
      produtos.forEach((produto) => {
        const categoriaProduto = produto.getAttribute("data-categoria");

        if (categoriaEscolhida === "todos" || categoriaProduto === categoriaEscolhida) {
          produto.classList.remove("escondido");
        } else {
          produto.classList.add("escondido");
        }
      });
    });
  });
});