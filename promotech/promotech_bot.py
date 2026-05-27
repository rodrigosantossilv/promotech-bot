

  


import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
from urllib.parse import quote
import json
import time
import os

# =========================================================
# CONFIG
# =========================================================

TELEGRAM_TOKEN = "8859168984:AAH8nvexWLrbVjGX46cDSfzaCEteUkFNELs"

CANAL_ID = "@promotechbrasil01"

PUBLISHER_ID = "XHKT38-E62C"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}

CATEGORIAS = [

    "ssd",
    "placa de video",
    "rx 7600",
    "rtx 4060",
    "processador",
    "ryzen 5",
    "notebook gamer",
    "mouse gamer",
    "monitor gamer",
    "teclado mecanico",
    "headset gamer",
    "pc gamer"

]

ARQUIVO = "enviados.json"

session = requests.Session()

# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)

@app.route("/")
def home():

    return "PromoTech Bot Online!"

# =========================================================
# CARREGAR
# =========================================================

def carregar():

    try:

        with open(ARQUIVO, "r") as f:

            return json.load(f)

    except:

        return []

# =========================================================
# SALVAR
# =========================================================

def salvar(lista):

    with open(ARQUIVO, "w") as f:

        json.dump(lista[-5000:], f)

# =========================================================
# LINK AFILIADO
# =========================================================

def gerar_link(link):

    if "?" in link:

        return (
            f"{link}"
            f"&matt_tool={PUBLISHER_ID}"
            f"&matt_source=telegram"
        )

    return (
        f"{link}"
        f"?matt_tool={PUBLISHER_ID}"
        f"&matt_source=telegram"
    )

# =========================================================
# TELEGRAM
# =========================================================

def enviar(msg):

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_TOKEN}/sendMessage"
        )

        payload = {

            "chat_id": CANAL_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": False

        }

        r = session.post(

            url,
            json=payload,
            timeout=30

        )

        print(
            f"TELEGRAM: {r.status_code}",
            flush=True
        )

        return r.status_code == 200

    except Exception as e:

        print(
            f"ERRO TELEGRAM: {e}",
            flush=True
        )

        return False

# =========================================================
# BUSCAR ML
# =========================================================

def buscar(termo):

    try:

        url = (
            "https://lista.mercadolivre.com.br/"
            f"{quote(termo)}"
        )

        r = session.get(

            url,
            headers=HEADERS,
            timeout=30

        )

        print(
            f"ML STATUS ({termo}): "
            f"{r.status_code}",
            flush=True
        )

        if r.status_code != 200:

            return []

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        cards = soup.select(
            ".ui-search-result"
        )

        print(
            f"ENCONTRADOS ({termo}): "
            f"{len(cards)}",
            flush=True
        )

        produtos = []

        for card in cards[:5]:

            try:

                titulo = card.select_one(
                    ".poly-component__title"
                )

                link = card.select_one("a")

                preco = card.select_one(
                    ".andes-money-amount__fraction"
                )

                if not titulo or not link:

                    continue

                valor = "0"

                if preco:

                    valor = preco.text.strip()

                produtos.append({

                    "id": link["href"],

                    "titulo": titulo.text.strip(),

                    "valor": valor,

                    "link": link["href"]

                })

            except:
                pass

        return produtos

    except Exception as e:

        print(
            f"ERRO ML: {e}",
            flush=True
        )

        return []

# =========================================================
# PROCESSAR
# =========================================================

def processar(produto, enviados):

    try:

        if produto["id"] in enviados:

            return

        link = gerar_link(
            produto["link"]
        )

        msg = (

            "🔥 <b>OFERTA TECH</b>\n\n"

            f"📌 <b>{produto['titulo']}</b>\n\n"

            f"💰 <b>R$ {produto['valor']}</b>\n\n"

            f"🛒 <a href='{link}'>"
            f"COMPRAR AGORA"
            f"</a>\n\n"

            "#PromoTech #Tecnologia"

        )

        ok = enviar(msg)

        if ok:

            enviados.append(
                produto["id"]
            )

            salvar(enviados)

            print(
                f"ENVIADO: "
                f"{produto['titulo']}",
                flush=True
            )

    except Exception as e:

        print(
            f"ERRO PROCESSAR: {e}",
            flush=True
        )

# =========================================================
# LOOP BOT
# =========================================================

def executar():

    print(
        "BOT ONLINE",
        flush=True
    )

    enviados = carregar()

    try:

        ok = enviar(

            "🤖 <b>PromoTech iniciado!</b>\n\n"
            "🔥 Monitorando ofertas automaticamente."

        )

        print(
            f"TELEGRAM TESTE: {ok}",
            flush=True
        )

    except Exception as e:

        print(
            f"ERRO TELEGRAM: {e}",
            flush=True
        )

    while True:

        print(
            "LOOP RODANDO",
            flush=True
        )

        try:

            for categoria in CATEGORIAS:

                print(
                    f"BUSCANDO: {categoria}",
                    flush=True
                )

                produtos = buscar(
                    categoria
                )

                for produto in produtos:

                    processar(
                        produto,
                        enviados
                    )

                    time.sleep(5)

                time.sleep(3)

        except Exception as e:

            print(
                f"ERRO LOOP: {e}",
                flush=True
            )

            time.sleep(10)

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    Thread(
        target=executar,
        daemon=True
    ).start()

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )