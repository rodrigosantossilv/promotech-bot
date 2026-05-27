import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from urllib.parse import quote
from flask import Flask
from threading import Thread
import os

# ============================================================
# CONFIGURAÇÕES
# ============================================================

TELEGRAM_TOKEN = "8859168984:AAH8nvexWLrbVjGX46cDSfzaCEteUkFNELs"

CANAL_ID = "@promotechbrasil01"

PUBLISHER_ID = "silvarodri20221029134247"

CATEGORIAS = [

    "ssd",
    "placa de video",
    "rx 7600",
    "rtx 4060",
    "processador",
    "ryzen",
    "notebook gamer",
    "monitor gamer",
    "mouse gamer",
    "teclado mecanico",
    "headset gamer",
    "pc gamer"

]

ARQUIVO = "enviados.json"

# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)

@app.route("/")
def home():

    return "PromoTech Bot Online!"

# ============================================================
# SESSION
# ============================================================

session = requests.Session()

HEADERS = {

    "User-Agent": (

        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"

    )

}

# ============================================================
# CARREGAR
# ============================================================

def carregar():

    try:

        with open(ARQUIVO, "r") as f:
            return json.load(f)

    except:

        return []

# ============================================================
# SALVAR
# ============================================================

def salvar(lista):

    with open(ARQUIVO, "w") as f:

        json.dump(lista[-5000:], f)

# ============================================================
# LINK AFILIADO
# ============================================================

def afiliado(link):

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

# ============================================================
# FORMATAR PREÇO
# ============================================================

def preco(v):

    try:

        return (

            f"R$ {float(v):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")

        )

    except:

        return "R$ 0,00"

# ============================================================
# BUSCAR PRODUTOS
# ============================================================

def buscar(termo):

    try:

        url = (
            "https://lista.mercadolivre.com.br/"
            f"{quote(termo)}"
        )

        response = session.get(

            url,
            headers=HEADERS,
            timeout=30

        )

        print(
            f"📡 STATUS ML ({termo}): "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            return []

        soup = BeautifulSoup(

            response.text,
            "html.parser"

        )

        produtos = []

        cards = soup.select(
            ".ui-search-result"
        )

        print(
            f"🔍 {termo}: "
            f"{len(cards)} encontrados"
        )

        for card in cards[:10]:

            try:

                titulo = card.select_one(
                    ".poly-component__title"
                )

                link = card.select_one("a")

                valor = card.select_one(
                    ".andes-money-amount__fraction"
                )

                if not titulo or not link:

                    continue

                preco_num = 0

                if valor:

                    preco_num = float(

                        valor.text
                        .replace(".", "")

                    )

                produtos.append({

                    "id": link["href"],

                    "title": titulo.text.strip(),

                    "price": preco_num,

                    "link": link["href"]

                })

            except:
                pass

        return produtos

    except Exception as e:

        print(f"❌ ERRO ML: {e}")

        return []

# ============================================================
# TELEGRAM
# ============================================================

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

        response = session.post(

            url,
            json=payload,
            timeout=30

        )

        print(
            f"📨 Telegram: "
            f"{response.status_code}"
        )

        return response.status_code == 200

    except Exception as e:

        print(f"❌ Telegram erro: {e}")

        return False

# ============================================================
# PROCESSAR PRODUTO
# ============================================================

def processar(produto, enviados):

    try:

        pid = produto["id"]

        if pid in enviados:

            return False

        titulo = produto["title"]

        valor = produto["price"]

        link = afiliado(
            produto["link"]
        )

        mensagem = (

            "💻 <b>PRODUTO TECH</b>\n\n"

            f"📌 <b>{titulo}</b>\n\n"

            f"💰 <b>{preco(valor)}</b>\n\n"

            f"🛒 <a href='{link}'>"
            f"👉 VER PRODUTO"
            f"</a>\n\n"

            "#PromoTech #Tecnologia"

        )

        ok = enviar(mensagem)

        if ok:

            enviados.append(pid)

            salvar(enviados)

            print(
                f"✅ ENVIADO: "
                f"{titulo[:50]}"
            )

            return True

    except Exception as e:

        print(f"❌ Produto erro: {e}")

    return False

# ============================================================
# LOOP BOT
# ============================================================


            def executar():

    print("🚀 BOT ONLINE")

    enviados = carregar()

    try:

        ok = enviar(

            "🤖 <b>PromoTech iniciado!</b>\n\n"
            "🔥 Monitorando ofertas automaticamente."

        )

        print(f"📨 TESTE TELEGRAM: {ok}")

    except Exception as e:

        print(f"❌ TELEGRAM ERRO: {e}")

    while True:

        try:

            print(
                f"\n⏰ "
                f"{datetime.now().strftime('%H:%M:%S')}"
            )

            for categoria in CATEGORIAS:

                print(f"🔍 BUSCANDO: {categoria}")

                produtos = buscar(categoria)

                print(
                    f"📦 PRODUTOS: "
                    f"{len(produtos)}"
                )

                for produto in produtos:

                    processar(
                        produto,
                        enviados
                    )

                    time.sleep(3)

                time.sleep(2)

        except Exception as e:

            print(f"❌ ERRO LOOP: {e}")

            time.sleep(15)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    # inicia bot em thread separada
    Thread(

        target=executar,
        daemon=True

    ).start()

    # flask principal
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