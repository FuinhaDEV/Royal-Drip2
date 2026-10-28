import logging
import os
import re
import secrets
from functools import wraps

import mysql.connector
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("royal_drip")

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    log.warning(
        "SECRET_KEY não definida: usando chave temporária (as sessões se "
        "perdem ao reiniciar). Defina a variável em produção."
    )
app.secret_key = SECRET_KEY

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
)

EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
NOME_REGEX = r"[A-Za-zÀ-ÿ\s]{3,100}"


# ----------------------------------------------------------------------------
# BANCO DE DADOS
# ----------------------------------------------------------------------------
def conectar_mysql():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "senai105"),
        database=os.environ.get("DB_NAME", "ROYAL_DRIP_SQL"),
    )


# ----------------------------------------------------------------------------
# PRODUTOS (IDs 1 a 39 Reorganizados)
# ----------------------------------------------------------------------------
PRODUTOS = {
    # CAMISETAS (IDs 1 a 6)
    1: {
        "id": 1,
        "nome": "camisa boxy dark angel drop1",
        "titulo": "Camisa Boxy Dark Angel Drop 01",
        "preco": 129.90,
        "imagem": "imagens/camisas/camisa 1.webp",
        "descricao": "Modelagem ampla com corte streetwear moderno, algodão encorpado e acabamento premium.",
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
        "imagem": "imagens/camisas/camisa 2.webp",
        "descricao": "Corte oversized com visual urbano, estampa marcante e tecido confortável.",
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
        "imagem": "imagens/camisas/camisa 3.webp",
        "descricao": "Edição leve com visual clean, caimento amplo e acabamento premium.",
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
        "nome": "camisa boxy brasilian once",
        "titulo": "Camisa Boxy Brasilian Once",
        "preco": 139.90,
        "imagem": "imagens/camisas/camisa boxy brasilian once.webp",
        "descricao": "Camisa Boxy Brasilian Once com estampa exclusiva e caimento oversized.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Camisetas",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 113, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 114, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 115, "L": 40},
        ],
    },
    5: {
        "id": 5,
        "nome": "camisa boxy come in",
        "titulo": "Camisa Boxy Come In",
        "preco": 139.90,
        "imagem": "imagens/camisas/camisa boxy come in.webp",
        "descricao": "Camisa Boxy Come In com estampa urbana e tecido encorpado.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Camisetas",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 113, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 114, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 115, "L": 40},
        ],
    },
    6: {
        "id": 6,
        "nome": "camisa boxy good plan",
        "titulo": "Camisa Boxy Good Plan",
        "preco": 139.90,
        "imagem": "imagens/camisas/camisa boxy good plan.webp",
        "descricao": "Camisa Boxy Good Plan com caimento streetwear amplo.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Camisetas",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 113, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 114, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 115, "L": 40},
        ],
    },

    # CONJUNTOS (IDs 7 a 12)
    7: {
        "id": 7,
        "nome": "conjunto cinza street drop1",
        "titulo": "Conjunto Cinza Street Drop 01",
        "preco": 289.90,
        "imagem": "imagens/blusas_Conjuntos/conjunto moletom cinza.webp",
        "descricao": "Moletom pesado com capuz e calça em modelo confortável.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 111, "L": 36.5},
            {"tamanho": "M", "Q": 85.5, "A": 112, "L": 37.5},
            {"tamanho": "G", "Q": 93, "A": 113, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
        ],
    },
    8: {
        "id": 8,
        "nome": "conjunto UK drop2",
        "titulo": "Conjunto UK Drop 02",
        "preco": 299.90,
        "imagem": "imagens/blusas_Conjuntos/USA.webp",
        "descricao": "Visual urbano e com textura premium.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 82.5, "A": 109, "L": 35.5},
            {"tamanho": "M", "Q": 84.5, "A": 110, "L": 36.5},
            {"tamanho": "G", "Q": 91, "A": 112, "L": 37.5},
            {"tamanho": "GG", "Q": 94, "A": 112, "L": 38.5},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 40},
        ],
    },
    9: {
        "id": 9,
        "nome": "conjunto branco street drop3",
        "titulo": "Conjunto Branco Street Drop 03",
        "preco": 319.90,
        "imagem": "imagens/blusas_Conjuntos/conjunto branco copy.webp",
        "descricao": "Estilo minimalista com acabamento refinado e tecido macio.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 113, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 113, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 114, "L": 40.5},
        ],
    },
    10: {
        "id": 10,
        "nome": "conjunto blue street drop4",
        "titulo": "Conjunto Blue Street Drop 04",
        "preco": 329.90,
        "imagem": "imagens/blusas_Conjuntos/conj2.webp",
        "descricao": "Conjunto em tom azul com visual esportivo e premium.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 82, "A": 109, "L": 35.5},
            {"tamanho": "M", "Q": 84, "A": 110, "L": 36.5},
            {"tamanho": "G", "Q": 90, "A": 111, "L": 37.5},
            {"tamanho": "GG", "Q": 93, "A": 112, "L": 38.5},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 39.5},
        ],
    },
    11: {
        "id": 11,
        "nome": "conjunto camuflado street drop5",
        "titulo": "Conjunto Camuflado Street Drop 05",
        "preco": 339.90,
        "imagem": "imagens/blusas_Conjuntos/conj3.webp",
        "descricao": "Estampa camuflada com visual robusto e capuz reforçado.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 84, "A": 110, "L": 36.5},
            {"tamanho": "M", "Q": 86, "A": 111, "L": 37.5},
            {"tamanho": "G", "Q": 92, "A": 112, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
        ],
    },
    12: {
        "id": 12,
        "nome": "conjunto cimento street drop6",
        "titulo": "Conjunto Cimento Street Drop 06",
        "preco": 349.90,
        "imagem": "imagens/blusas_Conjuntos/conj4.webp",
        "descricao": "Tom cimento com acabamento refinado e caimento largo.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Conjuntos",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85.5, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 112, "L": 38},
            {"tamanho": "GG", "Q": 96, "A": 113, "L": 39},
            {"tamanho": "XG", "Q": 100, "A": 114, "L": 40},
        ],
    },

    # CALÇAS (IDs 13 a 22)
    13: {
        "id": 13,
        "nome": "calça moletom lettering drop7",
        "titulo": "Calça de Moletom Lettering Drop 07",
        "preco": 239.90,
        "imagem": "imagens/calcas/Calça Moletom.webp",
        "descricao": "Calça de moletom com conforto premium e ajuste elástico.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "P", "Q": 83.5, "A": 111, "L": 36.5},
            {"tamanho": "M", "Q": 85.5, "A": 112, "L": 37.5},
            {"tamanho": "G", "Q": 93, "A": 113, "L": 38.5},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39.5},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 41},
        ],
    },
    14: {
        "id": 14,
        "nome": "calça moletom branca drop8",
        "titulo": "Calça de Moletom Branca Drop 08",
        "preco": 247.90,
        "imagem": "imagens/calcas/calça branca.webp",
        "descricao": "Visual clean e contemporâneo com tecido confortável.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "P", "Q": 82.5, "A": 109, "L": 35.5},
            {"tamanho": "M", "Q": 84.5, "A": 110, "L": 36.5},
            {"tamanho": "G", "Q": 91, "A": 111, "L": 37.5},
            {"tamanho": "GG", "Q": 94, "A": 112, "L": 38.5},
            {"tamanho": "XG", "Q": 98, "A": 113, "L": 40},
        ],
    },
    15: {
        "id": 15,
        "nome": "calça moletom azul drop9",
        "titulo": "Calça de Moletom Azul Drop 09",
        "preco": 249.90,
        "imagem": "imagens/calcas/calça azul.webp",
        "descricao": "Corte esportivo versátil e toque macio.",
        "tamanhos": ["P", "M", "G", "GG", "XG"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "P", "Q": 83, "A": 110, "L": 36},
            {"tamanho": "M", "Q": 85, "A": 111, "L": 37},
            {"tamanho": "G", "Q": 92, "A": 112, "L": 38},
            {"tamanho": "GG", "Q": 95, "A": 113, "L": 39},
            {"tamanho": "XG", "Q": 99, "A": 114, "L": 40.5},
        ],
    },
    16: {
        "id": 16,
        "nome": "calça jeans baggy hard",
        "titulo": "Calça Jeans Baggy Hard",
        "preco": 269.90,
        "imagem": "imagens/calcas/calça jeans hard 2.webp",
        "descricao": "Modelagem baggy com jeans encorpado de alta gramatura.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 80, "A": 108, "L": 34},
            {"tamanho": "40", "Q": 84, "A": 110, "L": 35},
            {"tamanho": "42", "Q": 88, "A": 112, "L": 36},
            {"tamanho": "44", "Q": 92, "A": 114, "L": 37},
            {"tamanho": "46", "Q": 96, "A": 115, "L": 38},
        ],
    },
    17: {
        "id": 17,
        "nome": "calça jeans baggy worn out",
        "titulo": "Calça Jeans Baggy Worn Out",
        "preco": 279.90,
        "imagem": "imagens/calcas/calça jeans hard.webp",
        "descricao": "Visual vintage desgastado com estampa streetwear marcante.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 81, "A": 108, "L": 34.5},
            {"tamanho": "40", "Q": 85, "A": 110, "L": 35.5},
            {"tamanho": "42", "Q": 89, "A": 112, "L": 36.5},
            {"tamanho": "44", "Q": 93, "A": 114, "L": 37.5},
            {"tamanho": "46", "Q": 97, "A": 115, "L": 38.5},
        ],
    },
    18: {
        "id": 18,
        "nome": "calça regular bless",
        "titulo": "Calça Regular Bless",
        "preco": 259.90,
        "imagem": "imagens/calcas/calça regular bless.webp",
        "descricao": "Corte reto contemporâneo com apliques em alto relevo.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 80, "A": 107, "L": 33},
            {"tamanho": "40", "Q": 84, "A": 109, "L": 34},
            {"tamanho": "42", "Q": 88, "A": 111, "L": 35},
            {"tamanho": "44", "Q": 92, "A": 113, "L": 36},
            {"tamanho": "46", "Q": 96, "A": 114, "L": 37},
        ],
    },
    19: {
        "id": 19,
        "nome": "calça jeans sant",
        "titulo": "Calça Jeans Sant",
        "preco": 289.90,
        "imagem": "imagens/calcas/calça jeans sant.webp",
        "descricao": "Estampa sacra oversized impressa em jeans escuro.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 82, "A": 109, "L": 35},
            {"tamanho": "40", "Q": 86, "A": 111, "L": 36},
            {"tamanho": "42", "Q": 90, "A": 113, "L": 37},
            {"tamanho": "44", "Q": 94, "A": 115, "L": 38},
            {"tamanho": "46", "Q": 98, "A": 116, "L": 39},
        ],
    },
    20: {
        "id": 20,
        "nome": "calça jeans barrel",
        "titulo": "Calça Jeans Barrel",
        "preco": 249.90,
        "imagem": "imagens/calcas/calça jeans barrel.webp",
        "descricao": "Modelagem Barrel curvada nas pernas com tom jeans escuro.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 79, "A": 106, "L": 34},
            {"tamanho": "40", "Q": 83, "A": 108, "L": 35},
            {"tamanho": "42", "Q": 87, "A": 110, "L": 36},
            {"tamanho": "44", "Q": 91, "A": 112, "L": 37},
            {"tamanho": "46", "Q": 95, "A": 113, "L": 38},
        ],
    },
    21: {
        "id": 21,
        "nome": "calça baggy nation",
        "titulo": "Calça Baggy Nation",
        "preco": 299.90,
        "imagem": "imagens/calcas/calça baggy nation.webp",
        "descricao": "Corte oversized com tipografia Nation gravada ao longo da perna.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 82, "A": 110, "L": 35.5},
            {"tamanho": "40", "Q": 86, "A": 112, "L": 36.5},
            {"tamanho": "42", "Q": 90, "A": 114, "L": 37.5},
            {"tamanho": "44", "Q": 94, "A": 115, "L": 38.5},
            {"tamanho": "46", "Q": 98, "A": 116, "L": 39.5},
        ],
    },
    22: {
        "id": 22,
        "nome": "calça jeans baggy camuflada",
        "titulo": "Calça Jeans Baggy Camuflada",
        "preco": 269.90,
        "imagem": "imagens/calcas/calça baggy camuflada.webp",
        "descricao": "Estampa camuflada militar em sarja encorpada com modelagem bem larga.",
        "tamanhos": ["38", "40", "42", "44", "46"],
        "categoria": "Calças",
        "medidas": [
            {"tamanho": "38", "Q": 81, "A": 108, "L": 35},
            {"tamanho": "40", "Q": 85, "A": 110, "L": 36},
            {"tamanho": "42", "Q": 89, "A": 112, "L": 37},
            {"tamanho": "44", "Q": 93, "A": 114, "L": 38},
            {"tamanho": "46", "Q": 97, "A": 115, "L": 39},
        ],
    },

    # GORROS (IDs 23 a 27)
    23: {
        "id": 23,
        "nome": "gorro oncinha y2k",
        "titulo": "Gorro Oncinha Y2K",
        "preco": 79.90,
        "imagem": "imagens/gorros/gorro oncinha y2k.webp",
        "descricao": "Gorro em tricô macio com estampa animal print Y2K.",
        "tamanhos": ["Único"],
        "categoria": "Gorros",
        "medidas": [{"tamanho": "Único", "Q": 54, "A": 22, "L": 20}],
    },
    24: {
        "id": 24,
        "nome": "gorro pré cort",
        "titulo": "Gorro Pré Cort",
        "preco": 89.90,
        "imagem": "imagens/gorros/gorro pré cort.webp",
        "descricao": "Gorro em malha encorpada preta com bordado frontal amplo.",
        "tamanhos": ["Único"],
        "categoria": "Gorros",
        "medidas": [{"tamanho": "Único", "Q": 54, "A": 22, "L": 20}],
    },
    25: {
        "id": 25,
        "nome": "gorro y2k black",
        "titulo": "Gorro Y2K Black",
        "preco": 79.90,
        "imagem": "imagens/gorros/gorro y2k black.webp",
        "descricao": "Gorro preto minimalista estilo Y2K.",
        "tamanhos": ["Único"],
        "categoria": "Gorros",
        "medidas": [{"tamanho": "Único", "Q": 54, "A": 22, "L": 20}],
    },
    26: {
        "id": 26,
        "nome": "gorro y2k white",
        "titulo": "Gorro Y2K White",
        "preco": 79.90,
        "imagem": "imagens/gorros/gorro y2k white.webp",
        "descricao": "Edição branca em lã macia com estampa frontal estilo graffiti.",
        "tamanhos": ["Único"],
        "categoria": "Gorros",
        "medidas": [{"tamanho": "Único", "Q": 54, "A": 22, "L": 20}],
    },
    27: {
        "id": 27,
        "nome": "gorro white red",
        "titulo": "Gorro White Red",
        "preco": 84.90,
        "imagem": "imagens/gorros/gorro white red.webp",
        "descricao": "Gorro com estampa em contraste vermelho e branco.",
        "tamanhos": ["Único"],
        "categoria": "Gorros",
        "medidas": [{"tamanho": "Único", "Q": 54, "A": 22, "L": 20}],
    },

    # CINTOS (IDs 28 a 39)
    28: {
        "id": 28,
        "nome": "cinto blue star",
        "titulo": "Cinto Blue Star",
        "preco": 119.90,
        "imagem": "imagens/cintos/blue star.webp",
        "descricao": "Cinto cravejado com pedras azuis e fivela prateada em formato de estrela Y2K.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    29: {
        "id": 29,
        "nome": "cinto cravejado de caveira",
        "titulo": "Cinto Cravejado de Caveira",
        "preco": 129.90,
        "imagem": "imagens/cintos/cinto caveira.webp",
        "descricao": "Cinto preto em couro sintético premium com pedras brilhantes e fivela de caveira pirata.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    30: {
        "id": 30,
        "nome": "cinto fly heart",
        "titulo": "Cinto Fly Heart",
        "preco": 119.90,
        "imagem": "imagens/cintos/fly heart.webp",
        "descricao": "Cinto em estilo punk/streetwear com fivela em formato de coração alado metálico.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    31: {
        "id": 31,
        "nome": "cinto purple cup",
        "titulo": "Cinto Purple Cup",
        "preco": 124.90,
        "imagem": "imagens/cintos/purple cup.webp",
        "descricao": "Cinto roxo cravejado com fivela personalizada em liga metálica de alta resistência.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    32: {
        "id": 32,
        "nome": "red die",
        "titulo": "Red Die",
        "preco": 119.90,
        "imagem": "imagens/cintos/red die.webp",
        "descricao": "Cinto vermelho streetwear com detalhes metálicos e fivela marcante.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    33: {
        "id": 33,
        "nome": "stelar white",
        "titulo": "Stelar White",
        "preco": 119.90,
        "imagem": "imagens/cintos/stelar white.webp",
        "descricao": "Cinto branco com fivelas e tachas metálicas em formato de estrela.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    34: {
        "id": 34,
        "nome": "camuflado",
        "titulo": "Cinto Camuflado",
        "preco": 119.90,
        "imagem": "imagens/cintos/cinto camuflado.webp",
        "descricao": "Cinto camuflado com a fivela personalizada com escritas douradas.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    35: {
        "id": 35,
        "nome": "swag branco",
        "titulo": "Cinto Swag Branco",
        "preco": 119.90,
        "imagem": "imagens/cintos/cinto swag branco.webp",
        "descricao": "Cinto branco com fivelas e tachas metálicas em formato de ST.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    36: {
        "id": 36,
        "nome": "swag preto",
        "titulo": "Cinto Swag Preto",
        "preco": 119.90,
        "imagem": "imagens/cintos/cinto swag preto.webp",
        "descricao": "Cinto preto com fivelas e tachas metálicas em formato de ST.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    37: {
        "id": 37,
        "nome": "lunar bl",
        "titulo": "Cinto Lunar BL",
        "preco": 119.90,
        "imagem": "imagens/cintos/cinto lunar bl.webp",
        "descricao": "Cinto preto com fivelas e tachas metálicas em formato de lua.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    38: {
        "id": 38,
        "nome": "marrom star",
        "titulo": "Cinto Marrom Star",
        "preco": 119.90,
        "imagem": "imagens/cintos/cinto marrom star.webp",
        "descricao": "Cinto marrom com fivelas e tachas metálicas em formato de estrela.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
    39: {
        "id": 39,
        "nome": "cinto couro cowboy",
        "titulo": "Cinto Couro Cowboy",
        "preco": 119.90,
        "imagem": "imagens/cintos/cinto couro cowboy.webp",
        "descricao": "Cinto de couro cowboy com fivelas e tachas metálicas.",
        "tamanhos": ["Único"],
        "categoria": "Cintos",
        "medidas": [{"tamanho": "Único"}],
    },
}


# ----------------------------------------------------------------------------
# IMAGENS: usa .webp quando existir; senão cai para o arquivo original
# ----------------------------------------------------------------------------
EXTENSOES_IMAGEM = (".webp", ".jpeg", ".jpg", ".jpe", ".jfif", ".png")


def resolver_imagem(caminho):
    """Recebe 'imagens/cintos/blue star.webp' e devolve o arquivo que realmente
    existe em static/ (mesmo nome com outra extensão ou outra caixa de letras).
    Se nada for encontrado, devolve o caminho original."""
    pasta_rel, _, nome = caminho.rpartition("/")
    pasta = os.path.join(app.static_folder, *pasta_rel.split("/"))
    base = os.path.splitext(nome)[0].lower()
    # aceita grafias alternativas do mesmo arquivo (ex.: cowboy/cawboy)
    bases = {base, base.replace("cowboy", "cawboy"), base.replace("cawboy", "cowboy")}

    try:
        arquivos = os.listdir(pasta)
    except OSError:
        return caminho

    candidatos = {}
    for arq in arquivos:
        raiz, ext = os.path.splitext(arq)
        if raiz.lower() in bases and ext.lower() in EXTENSOES_IMAGEM:
            candidatos[ext.lower()] = arq

    for ext in EXTENSOES_IMAGEM:  # prioridade: webp > jpeg > jpg > png
        if ext in candidatos:
            return f"{pasta_rel}/{candidatos[ext]}"
    return caminho


@app.template_global()
def img_url(caminho):
    return resolver_imagem(caminho)


for _p in PRODUTOS.values():
    _p["imagem"] = resolver_imagem(_p["imagem"])


# ----------------------------------------------------------------------------
# AUXILIARES
# ----------------------------------------------------------------------------
def login_obrigatorio(func):
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


def verificar_imagens():
    """Avisa no log se algum produto aponta para uma imagem que não existe."""
    base = os.path.join(app.static_folder)
    faltando = [
        (pid, p["imagem"])
        for pid, p in PRODUTOS.items()
        if not os.path.isfile(os.path.join(base, *p["imagem"].split("/")))
    ]
    usando_original = [
        (pid, p["imagem"]) for pid, p in PRODUTOS.items()
        if not p["imagem"].lower().endswith(".webp")
    ]
    for pid, caminho in usando_original:
        log.info("Produto %s usando original (sem .webp): static/%s", pid, caminho)
    for pid, caminho in faltando:
        log.warning("IMAGEM NAO ENCONTRADA (produto %s): static/%s", pid, caminho)
    if not faltando:
        log.info("Todas as imagens dos produtos foram encontradas.")


# ----------------------------------------------------------------------------
# ROTAS
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

        return redirect(url_for("login"))

    return render_template("registro.html")


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
                log.exception("Hash de senha inválido para %s", email)

        if senha_ok:
            session.clear()
            iniciar_sessao(usuario)
            return redirect(url_for("index"))

        return render_template("login.html", erros=["E-mail ou senha incorretos."])

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/carrinho/adicionar", methods=["POST"])
@login_obrigatorio
def adicionar_carrinho():
    produto_id = request.form.get("produto_id", type=int)
    tamanho = request.form.get("tamanho", "")

    if produto_id is None or produto_id not in PRODUTOS:
        return "Produto inválido", 400

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
        cursor.execute(
            "DELETE FROM carrinho WHERE id_carrinho = %s AND id_usuario = %s",
            (id_carrinho, session["usuario_id"]),
        )
        conexao.commit()
    except mysql.connector.Error:
        log.exception("Erro ao remover item do carrinho")
        if conexao:
            conexao.rollback()
        return "Não foi possível remover o item.", 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    return redirect(url_for("carrinho"))


if __name__ == "__main__":
    verificar_imagens()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")