import logging
import os
import re
from functools import wraps

import mysql.connector
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Em produção, defina estas variáveis de ambiente (os valores abaixo são só para desenvolvimento).
app.secret_key = os.environ.get("SECRET_KEY", "royal_drip_dev_key_troque_em_producao")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("royal_drip")

EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
NOME_REGEX = r"[A-Za-zÀ-ÿ\s]{3,100}"


# ----------------------------------------------------------------------------
# BANCO DE DADOS (uma única função de conexão)
# ----------------------------------------------------------------------------
def conectar_mysql():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "senai105"),
        database=os.environ.get("DB_NAME", "ROYAL_DRIP_SQL"),
    )


# ----------------------------------------------------------------------------
# PRODUTOS (mesmos ids, nomes e preços da tabela `produtos` do SQL)
# ----------------------------------------------------------------------------
PRODUTOS = {
    1: {
        "id": 1,
        "nome": "camisa boxy dark angel drop1",
        "titulo": "Camisa Boxy Dark Angel Drop 01",
        "preco": 129.90,
        "imagem": "imagens/camisas/camisa 1.jpg",
        "descricao": "Modelagem ampla com corte streetwear moderno, algodão encorpado e acabamento premium para o dia a dia com atitude.",
        "tamanhos": ["P", "M", "G", "GG", "XG", "2XG"],
        "categoria": "Camisetas",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 111, "L": 36.5},
            {"tamanho": "M", "Q": 85.5, "A": 112, "L": 37.5},
            {"tamanho": "G", "Q": 93, "A": 113, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41},
        ],
    },
    2: {
        "id": 2,
        "nome": "camisa boxy black bite drop2",
        "titulo": "Camisa Boxy Black Bite Drop 02",
        "preco": 139.90,
        "imagem": "imagens/camisas/camisa 2.jpg",
        "descricao": "Corte oversized com visual urbano, estampa marcante e tecido confortável para uso diário.",
        "tamanhos": ["P", "M", "G", "GG", "XG", "2XG"],
        "categoria": "Camisetas",
        "medidas": [
            {"tamanho": "P", "Q": 82, "A": 108, "L": 35.5},
            {"tamanho": "M", "Q": 84, "A": 109, "L": 36.5},
            {"tamanho": "G", "Q": 90, "A": 112, "L": 38},
            {"tamanho": "GG", "Q": 94, "A": 112, "L": 39},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 40.5},
            {"tamanho": "2XG", "Q": 102, "A": 114, "L": 40.5},
        ],
    },
    3: {
        "id": 3,
        "nome": "camisa boxy light bite drop3",
        "titulo": "Camisa Boxy Light Bite Drop 03",
        "preco": 149.90,
        "imagem": "imagens/camisas/camisa 3.jpg",
        "descricao": "Edição leve com visual clean, caimento amplo e acabamento premium para compor looks street.",
        "tamanhos": ["P", "M", "G", "GG", "XG", "2XG"],
        "categoria": "Camisetas",
        "medidas": [
            {"tamanho": "P", "Q": 84, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 86, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 113, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 114, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 115, "L": 40},
            {"tamanho": "2XG", "Q": 104, "A": 116, "L": 40.5},
        ],
    },
    4: {
        "id": 4,
        "nome": "conjunto cinza street drop1",
        "titulo": "Conjunto Cinza Street Drop 01",
        "preco": 289.90,
        "imagem": "imagens/blusas_Conjuntos/conjunto moletom cinza.jpg",
        "descricao": "Moletom pesado com capuz e calça cargo em modelo confortável, ideal para clima frio e uso casual.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 111, "L": 36.5},
            {"tamanho": "M", "Q": 85.5, "A": 112, "L": 37.5},
            {"tamanho": "G", "Q": 93, "A": 113, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41},
        ],
    },
    5: {
        "id": 5,
        "nome": "conjunto UK drop2",
        "titulo": "Conjunto UK Drop 02",
        "preco": 299.90,
        "imagem": "imagens/blusas_Conjuntos/USA.jpg",
        "descricao": "Visual urbano e com textura premium, ideal para compor um outfit monotonal com presença elevada.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 82.5, "A": 109, "L": 35.5},
            {"tamanho": "M", "Q": 84.5, "A": 110, "L": 36.5},
            {"tamanho": "G", "Q": 91, "A": 112, "L": 37.5},
            {"tamanho": "GG", "Q": 94, "A": 112, "L": 38.5},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 40},
            {"tamanho": "2XG", "Q": 103, "A": 114, "L": 41},
        ],
    },
    6: {
        "id": 6,
        "nome": "conjunto branco street drop3",
        "titulo": "Conjunto Branco Street Drop 03",
        "preco": 319.90,
        "imagem": "imagens/blusas_Conjuntos/conjunto branco copy.jpg",
        "descricao": "Estilo minimalista com acabamento refinado, tecido macio e caimento confortável para o dia a dia.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 113, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 113, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 114, "L": 40.5},
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41},
        ],
    },
    7: {
        "id": 7,
        "nome": "conjunto blue street drop4",
        "titulo": "Conjunto Blue Street Drop 04",
        "preco": 329.90,
        "imagem": "imagens/blusas_Conjuntos/conj2.jpg",
        "descricao": "Conjunto em tom azul com visual esportivo e premium, pensado para quem busca presença e conforto.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 82, "A": 109, "L": 35.5},
            {"tamanho": "M", "Q": 84, "A": 110, "L": 36.5},
            {"tamanho": "G", "Q": 90, "A": 111, "L": 37.5},
            {"tamanho": "GG", "Q": 93, "A": 112, "L": 38.5},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 39.5},
            {"tamanho": "2XG", "Q": 102, "A": 114, "L": 40.5},
        ],
    },
    8: {
        "id": 8,
        "nome": "conjunto camuflado street drop5",
        "titulo": "Conjunto Camuflado Street Drop 05",
        "preco": 339.90,
        "imagem": "imagens/blusas_Conjuntos/conj3.jpg",
        "descricao": "Estampa camuflada com visual robusto, capuz reforçado e estrutura ideal para o clima urbano.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 84, "A": 110, "L": 36.5},
            {"tamanho": "M", "Q": 86, "A": 111, "L": 37.5},
            {"tamanho": "G", "Q": 92, "A": 112, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41.5},
        ],
    },
    9: {
        "id": 9,
        "nome": "conjunto cimento street drop6",
        "titulo": "Conjunto Cimento Street Drop 06",
        "preco": 349.90,
        "imagem": "imagens/blusas_Conjuntos/conj4.jpg",
        "descricao": "Tom cimento com acabamento refinado, caimento largo e visual sofisticado para uso frequente.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85.5, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 112, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 113, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 114, "L": 40},
            {"tamanho": "2XG", "Q": 105, "A": 115, "L": 41},
        ],
    },
    10: {
        "id": 10,
        "nome": "calça moletom letringg drop7",
        "titulo": "Calça de Moletom Letringg Drop 07",
        "preco": 239.90,
        "imagem": "imagens/calcas/Calça Moletom.jpg",
        "descricao": "Calça de moletom com conforto premium, elástico e modelagem moderna para um visual casual e estável.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 111, "L": 36.5},
            {"tamanho": "M", "Q": 85.5, "A": 112, "L": 37.5},
            {"tamanho": "G", "Q": 93, "A": 113, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41},
        ],
    },
    11: {
        "id": 11,
        "nome": "calça moletom branca drop8",
        "titulo": "Calça de Moletom Branca Drop 08",
        "preco": 247.90,
        "imagem": "imagens/calcas/calça branca.jpg",
        "descricao": "Visual clean e contemporâneo, com tecido confortável e ajuste que favorece a modelagem ampla.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "P", "Q": 82.5, "A": 109, "L": 35.5},
            {"tamanho": "M", "Q": 84.5, "A": 110, "L": 36.5},
            {"tamanho": "G", "Q": 91, "A": 111, "L": 37.5},
            {"tamanho": "GG", "Q": 94, "A": 112, "L": 38.5},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 40},
            {"tamanho": "2XG", "Q": 102, "A": 114, "L": 41},
        ],
    },
    12: {
        "id": 12,
        "nome": "calça moletom azul drop9",
        "titulo": "Calça de Moletom Azul Drop 09",
        "preco": 249.90,
        "imagem": "imagens/calcas/calça azul.jpg",
        "descricao": "Corte de calça com visual esportivo, acabamento versátil e toque macio para o uso diário.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 112, "L": 38},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 40.5},
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41},
        ],
    },
}

# Mantém só as medidas dos tamanhos que o produto realmente vende
# (ex.: os conjuntos não têm 2XG, então a medida 2XG some da tabela).
for _p in PRODUTOS.values():
    _p["medidas"] = [m for m in _p["medidas"] if m["tamanho"] in _p["tamanhos"]]


# ----------------------------------------------------------------------------
# AUXILIARES
# ----------------------------------------------------------------------------
def login_obrigatorio(func):
    """Redireciona para o login se o usuário não estiver logado."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def iniciar_sessao(usuario):
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]


# ----------------------------------------------------------------------------
# PÁGINAS
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/inicio")
def inicio():
    return render_template("inicio.html")


@app.route("/produto/<int:produto_id>")
def produto(produto_id):
    produto_selecionado = PRODUTOS.get(produto_id)

    if produto_selecionado is None:
        return "Produto não encontrado", 404

    return render_template("produto.html", produto=produto_selecionado)


# ----------------------------------------------------------------------------
# CADASTRO
# ----------------------------------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        cep = re.sub(r"\D", "", request.form.get("cep", ""))
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmarSenha", "")

        erros = []

        if not re.fullmatch(NOME_REGEX, nome):
            erros.append("Nome inválido. Use apenas letras e espaços (mínimo 3).")

        if not re.fullmatch(EMAIL_REGEX, email):
            erros.append("E-mail inválido.")

        telefone_numeros = re.sub(r"\D", "", telefone)
        if len(telefone_numeros) < 10 or len(telefone_numeros) > 11:
            erros.append("Telefone inválido. Deve ter 10 ou 11 dígitos.")

        if len(cep) != 8:
            erros.append("CEP inválido. Deve ter 8 números.")

        if len(senha) < 6:
            erros.append("A senha deve ter no mínimo 6 caracteres.")

        if senha != confirmar_senha:
            erros.append("As senhas não coincidem.")

        if erros:
            return render_template("registro.html", erros=erros)

        senha_hash = generate_password_hash(senha, method="pbkdf2:sha256")

        conexao = None
        cursor = None
        try:
            conexao = conectar_mysql()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, telefone, senha)
                VALUES (%s, %s, %s, %s)
                """,
                (nome, email, telefone_numeros, senha_hash),
            )
            conexao.commit()

        except mysql.connector.IntegrityError:
            if conexao:
                conexao.rollback()
            return render_template("registro.html", erros=["Este e-mail já está cadastrado."])
        except mysql.connector.Error:
            log.exception("Erro ao cadastrar usuário")
            if conexao:
                conexao.rollback()
            return render_template(
                "registro.html",
                erros=["Não foi possível concluir o cadastro. Tente novamente."],
            )
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

        # Cadastro concluído: volta para a tela de login
        return redirect(url_for("login"))

    return render_template("registro.html")


# ----------------------------------------------------------------------------
# LOGIN / LOGOUT
# ----------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        erros = []

        if not re.fullmatch(EMAIL_REGEX, email):
            erros.append("E-mail inválido.")

        if not senha:
            erros.append("Senha obrigatória.")

        if erros:
            return render_template("login.html", erros=erros)

        conexao = None
        cursor = None
        try:
            conexao = conectar_mysql()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, nome, email, senha FROM usuarios WHERE email = %s",
                (email,),
            )
            usuario = cursor.fetchone()
        except mysql.connector.Error:
            log.exception("Erro no login")
            return render_template(
                "login.html",
                erros=["Erro ao acessar o sistema. Tente novamente."],
            )
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

        senha_ok = False
        if usuario:
            try:
                senha_ok = check_password_hash(usuario["senha"], senha)
            except Exception:
                # hash em formato inválido/não suportado no banco
                log.exception("Hash de senha inválido para %s", email)

        if senha_ok:
            iniciar_sessao(usuario)
            return redirect(url_for("index"))

        if usuario is None:
            log.info("Login falhou: e-mail %s não existe no banco", email)
        else:
            log.info("Login falhou: senha incorreta para %s", email)

        return render_template("login.html", erros=["E-mail ou senha incorretos."])

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ----------------------------------------------------------------------------
# CARRINHO
# ----------------------------------------------------------------------------
@app.route("/carrinho/adicionar", methods=["POST"])
@login_obrigatorio
def adicionar_carrinho():
    produto_id = request.form.get("produto_id", type=int)
    tamanho = request.form.get("tamanho", "")

    if produto_id is None or produto_id not in PRODUTOS:
        return "Produto inválido", 400

    # O tamanho precisa existir NESTE produto (conjuntos não têm 2XG)
    if tamanho not in PRODUTOS[produto_id]["tamanhos"]:
        return "Tamanho inválido", 400

    quantidade = request.form.get("quantidade", type=int)
    if quantidade is None or quantidade < 1 or quantidade > 10:
        return "Quantidade inválida", 400

    conexao = None
    cursor = None
    try:
        conexao = conectar_mysql()
        cursor = conexao.cursor()

        # Mesmo produto + mesmo tamanho: soma a quantidade (máx. 10)
        cursor.execute(
            """
            INSERT INTO carrinho (id_usuario, id_produto, tamanho, quantidade)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE quantidade = LEAST(quantidade + %s, 10)
            """,
            (session["usuario_id"], produto_id, tamanho, quantidade, quantidade),
        )
        conexao.commit()
    except mysql.connector.Error:
        log.exception("Erro ao adicionar ao carrinho")
        if conexao:
            conexao.rollback()
        return "Não foi possível adicionar ao carrinho.", 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    return redirect(url_for("carrinho"))


@app.route("/carrinho")
@login_obrigatorio
def carrinho():
    conexao = None
    cursor = None
    linhas = []
    try:
        conexao = conectar_mysql()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_carrinho, id_produto, tamanho, quantidade
            FROM carrinho
            WHERE id_usuario = %s
            ORDER BY criado_em DESC
            """,
            (session["usuario_id"],),
        )
        linhas = cursor.fetchall()
    except mysql.connector.Error:
        log.exception("Erro ao carregar carrinho")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    itens = []
    total = 0.0
    for linha in linhas:
        p = PRODUTOS.get(linha["id_produto"])
        if p is None:
            continue
        subtotal = p["preco"] * linha["quantidade"]
        total += subtotal
        itens.append(
            {
                "id_carrinho": linha["id_carrinho"],
                "produto": p,
                "tamanho": linha["tamanho"],
                "quantidade": linha["quantidade"],
                "subtotal": subtotal,
            }
        )

    return render_template("carrinho.html", itens=itens, total=total)


@app.route("/carrinho/remover/<int:id_carrinho>", methods=["POST"])
@login_obrigatorio
def remover_carrinho(id_carrinho):
    conexao = None
    cursor = None
    try:
        conexao = conectar_mysql()
        cursor = conexao.cursor()
        # Filtra também pelo usuário: ninguém remove item do carrinho de outro
        cursor.execute(
            "DELETE FROM carrinho WHERE id_carrinho = %s AND id_usuario = %s",
            (id_carrinho, session["usuario_id"]),
        )
        conexao.commit()
    except mysql.connector.Error:
        log.exception("Erro ao remover item do carrinho")
        if conexao:
            conexao.rollback()
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    return redirect(url_for("carrinho"))


# ----------------------------------------------------------------------------
# PEDIDOS DOS CLIENTES (SELECT com INNER JOIN: pedidos + clientes)
# ----------------------------------------------------------------------------
@app.route("/pedidos")
def listar_pedidos():
    pedidos = []
    erro = None
    conexao = None
    cursor = None
    try:
        conexao = conectar_mysql()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.id_pedido, c.nome, c.cidade, c.estado,
                   p.data_pedido, p.valor_total, p.status_pedido
            FROM pedidos p
            INNER JOIN clientes c ON c.id_cliente = p.id_cliente
            ORDER BY p.data_pedido DESC
            """
        )
        pedidos = cursor.fetchall()
    except mysql.connector.Error:
        log.exception("Erro ao listar pedidos")
        erro = "Não foi possível carregar os pedidos. Tente novamente."
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    return render_template("pedidos.html", pedidos=pedidos, erro=erro)


# ----------------------------------------------------------------------------
# EXECUTAR
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "1") == "1")