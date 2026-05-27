import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
from urllib.parse import quote
import json
import time
import os

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = "SEU_TOKEN"
CANAL_ID = "@promotechbrasil01"

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
    "ryzen",
    "notebook gamer",
    "mouse gamer",
    "monitor gamer"
]

ARQUIVO = "enviados.json"

session = requests.Session()

# =========================
# FLASK
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "PromoTech Bot Online!"

# =========================
# SALVAR
# =========================

def carregar():

    try:
        with open(ARQUIVO, "r") as f:
            return json.load(f)

    except:
        return []

def salvar(lista):

    with open(ARQUIVO, "w") as f:
        json.dump(lista[-5000:], f)

# =========================
# TELEGRAM
# =========================

def enviar(msg):

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_TOKEN}/sendMessage"
        )

        payload = {
            "chat_id": CANAL_ID,
            "text": msg,
            "parse_mode": "HTML"
        }

        r = session.post(
            url,
            json=payload,
            timeout=30
        )

        print("TELEGRAM:", r.status_code)

        return r.status_code == 200

    except Exception as e:

        print("ERRO TELEGRAM:", e)

        return False

# =========================
# BUSCAR ML
# =========================

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

        print("ML STATUS:", r.status_code)

        if r.status_code != 200:
            return []

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        cards = soup.select(
            ".ui-search-result"
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

                valor = 0

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

        print("ERRO ML:", e)

        return []

# =========================
# BOT
# =========================

def executar():

    print("BOT ONLINE")

    enviados = carregar()

    enviar(
        "🤖 <b>PromoTech iniciado!</b>"
    )

    while True:

        try:

            for categoria in CATEGORIAS:

                print("BUSCANDO:", categoria)

                produtos = buscar(categoria)

                print("ENCONTRADOS:", len(produtos))

                for p in produtos:

                    if p["id"] in enviados:
                        continue

                    msg = (

                        "💻 <b>PRODUTO TECH</b>\n\n"

                        f"📌 <b>{p['titulo']}</b>\n\n"

                        f"💰 <b>R$ {p['valor']}</b>\n\n"

                        f"🛒 {p['link']}"

                    )

                    ok = enviar(msg)

                    if ok:

                        enviados.append(
                            p["id"]
                        )

                        salvar(enviados)

                        print(
                            "ENVIADO:",
                            p["titulo"]
                        )

                    time.sleep(5)

                time.sleep(3)

        except Exception as e:

            print("ERRO LOOP:", e)

            time.sleep(10)

# =========================
# START
# =========================

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