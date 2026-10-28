#!/usr/bin/env python3
"""
Diagnostica e repara as imagens dos produtos do site.

Le os caminhos "imagem" do app.py e, para cada um, verifica se o arquivo .webp
existe e e valido. Se nao for, procura na mesma pasta o arquivo original
(ignorando maiusculas, acentos, espacos e extensoes duplicadas como
"blue star.jpeg.jpg") e gera o .webp com o nome exato que o site espera.

Uso:
    pip install Pillow
    python reparar_imagens.py --dry-run     # so mostra o diagnostico
    python reparar_imagens.py               # diagnostica e repara
"""

import argparse
import difflib
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

PROJETO = Path(r"C:\Users\Aluno\Downloads\Seu projeto")
EXTS = (".webp", ".jpeg", ".jpg", ".jpe", ".jfif", ".png", ".gif", ".bmp", ".tif", ".tiff")


def norm(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def stem_limpo(nome: str) -> str:
    """Remove extensoes (inclusive duplicadas) do nome do arquivo."""
    p = Path(nome)
    while p.suffix.lower() in EXTS:
        p = p.with_suffix("")
    return p.name


def webp_valido(caminho: Path) -> bool:
    try:
        if not caminho.is_file() or caminho.stat().st_size == 0:
            return False
        with Image.open(caminho) as im:
            im.verify()
        return True
    except Exception:  # noqa: BLE001
        return False


def converter(origem: Path, destino: Path, qualidade: int) -> None:
    with Image.open(origem) as im:
        icc = im.info.get("icc_profile")
        im = ImageOps.exif_transpose(im)
        if im.mode == "P":
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        elif im.mode in ("LA", "PA"):
            im = im.convert("RGBA")
        elif im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        params = {"format": "WEBP", "quality": qualidade, "method": 6}
        if icc:
            params["icc_profile"] = icc
        tmp = destino.with_name(destino.name + ".tmp")
        im.save(tmp, **params)
    tmp.replace(destino)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, default=PROJETO / "app.py")
    ap.add_argument("--static", type=Path, default=PROJETO / "static")
    ap.add_argument("--quality", type=int, default=85)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.app.is_file():
        print(f"[erro] app.py nao encontrado: {args.app}")
        return 1
    if not args.static.is_dir():
        print(f"[erro] pasta static nao encontrada: {args.static}")
        return 1

    texto = args.app.read_text(encoding="utf-8")
    esperados = re.findall(r'"imagem":\s*"([^"]+)"', texto)
    print(f"{len(esperados)} imagens de produtos encontradas no app.py\n")

    ok = reparadas = 0
    problemas = []

    for rel in esperados:
        destino = args.static.joinpath(*rel.split("/"))
        pasta = destino.parent

        if webp_valido(destino):
            ok += 1
            continue

        motivo = "arquivo invalido/vazio" if destino.exists() else "arquivo nao existe"

        if not pasta.is_dir():
            problemas.append((rel, "pasta nao existe", []))
            print(f"[FALTA]  {rel}  (a pasta {pasta.name} nao existe)")
            continue

        alvo = norm(destino.stem)
        alvos = {alvo, alvo.replace("cowboy", "cawboy"), alvo.replace("cawboy", "cowboy")}
        candidatos = [
            f for f in pasta.iterdir()
            if f.is_file() and f != destino and f.suffix.lower() in EXTS
            and norm(stem_limpo(f.name)) in alvos
        ]
        candidatos.sort(key=lambda f: EXTS.index(f.suffix.lower()))

        if not candidatos:
            nomes = [f.stem for f in pasta.iterdir() if f.is_file()]
            parecidos = difflib.get_close_matches(destino.stem, nomes, n=3, cutoff=0.5)
            problemas.append((rel, motivo, parecidos))
            print(f"[FALTA]  {rel}  ({motivo}; nenhum original encontrado)")
            if parecidos:
                print(f"         nomes parecidos na pasta: {', '.join(parecidos)}")
            continue

        origem = candidatos[0]
        print(f"[repara] {rel}  <-  {origem.name}  ({motivo})")
        if args.dry_run:
            reparadas += 1
            continue
        try:
            converter(origem, destino, args.quality)
            reparadas += 1
        except Exception as exc:  # noqa: BLE001
            problemas.append((rel, f"falha ao converter {origem.name}: {exc}", []))
            print(f"[ERRO]   {rel}: {exc}")

    print("\n" + "=" * 55)
    print(f"OK: {ok} | Reparadas: {reparadas}{' (simulado)' if args.dry_run else ''} | Com problema: {len(problemas)}")
    if problemas:
        print("\nAinda precisam de atencao (coloque o arquivo na pasta com o nome indicado):")
        for rel, motivo, _ in problemas:
            print(f"  - static/{rel}  -> {motivo}")
    return 0 if not problemas else 2


if __name__ == "__main__":
    sys.exit(main())