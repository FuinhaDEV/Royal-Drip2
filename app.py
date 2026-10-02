from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import re
from werkzeug.security import generate_password_hash

app = Flask(__name__)


def conectar_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="senai105",  
        database="DADOS_ROYAL_DRIP"
    )

# Rota Principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

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
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 102, "A": 114, "L": 40.5}
        ]
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
            {"tamanho": "2XG", "Q": 104, "A": 116, "L": 40.5}
        ]
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
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 103, "A": 114, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 102, "A": 114, "L": 40.5}
        ]
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
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41.5}
        ]
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
            {"tamanho": "2XG", "Q": 105, "A": 115, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 102, "A": 114, "L": 41}
        ]
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
            {"tamanho": "2XG", "Q": 104, "A": 115, "L": 41}
        ]
    }
}

# Rota para o produto

@app.route("/produto/<int:produto_id>")
def produto(produto_id):

    produto_selecionado = PRODUTOS.get(produto_id)

    if produto_selecionado is None:
        return "Produto não encontrado", 404

    return render_template(
        "produto.html",
        produto=produto_selecionado
    )

# CADASTRO

@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        senha = request.form.get("senha", "")

        erros = []

        # Nome
        if not re.fullmatch(
            r"[A-Za-zÀ-ÿ\s]{3,100}",
            nome
        ):
            erros.append(
                "Nome inválido. Use apenas letras e espaços."
            )

        # E-mail
        if not re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        ):
            erros.append("E-mail inválido.")

        # Telefone
        if not re.fullmatch(
            r"\([0-9]{2}\)\s?[0-9]{5}-[0-9]{4}",
            telefone
        ):
            erros.append(
                "Telefone inválido. Use o formato (11) 96666-7777."
            )

        # Senha
        if not re.fullmatch(
            r"(?=.*[A-Za-z])(?=.*[0-9]).{8,72}",
            senha
        ):
            erros.append(
                "A senha deve ter entre 8 e 72 caracteres "
                "e conter letras e números."
            )

        if erros:
            return render_template(
                "registro.html",
                erros=erros
            )

        senha_hash = generate_password_hash(senha)

        conexao = conectar_mysql()
        cursor = conexao.cursor()

        try:

            sql = """
                INSERT INTO usuarios
                (nome, email, telefone, senha)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                sql,
                (nome, email, telefone, senha_hash)
            )

            conexao.commit()

        except mysql.connector.IntegrityError:

            conexao.rollback()

            return render_template(
                "registro.html",
                erros=["Este e-mail já está cadastrado."]
            )

        finally:

            cursor.close()
            conexao.close()

        return redirect(url_for("index"))

    return render_template("registro.html")
@app.route("/carrinho/adicionar", methods=["POST"])
def adicionar_carrinho():

    produto_id = request.form.get("produto_id")
    tamanho = request.form.get("tamanho")
    quantidade = request.form.get("quantidade")

    if not produto_id:
        return "Produto não informado", 400

    if tamanho not in ["P", "M", "G", "GG", "XG", "2XG"]:
        return "Tamanho inválido", 400

    try:

        quantidade = int(quantidade)

        if quantidade < 1 or quantidade > 10:
            return "Quantidade inválida", 400

    except (TypeError, ValueError):

        return "Quantidade inválida", 400

    conexao = conectar_mysql()
    cursor = conexao.cursor()

    try:

        sql = """
            INSERT INTO carrinho
            (produto_id, tamanho, quantidade)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            sql,
            (produto_id, tamanho, quantidade)
        )

        conexao.commit()

    finally:

        cursor.close()
        conexao.close()

    return redirect(url_for("carrinho"))


#carrinho

@app.route("/carrinho")
def carrinho():

    return render_template("carrinho.html")

#executar tudo isso
#conectar MYSQL 
def conectar_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="senai105",
        database="DADOS_ROYAL_DRIP"
    )

if __name__ == "__main__":
    app.run(debug=True)