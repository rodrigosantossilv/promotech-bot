import requests
import time
import threading
from flask import Flask

# =====================================================
# CONFIG
# =====================================================

TELEGRAM_TOKEN = "8859168984:AAH8nvexWLrbVjGX46cDSfzaCEteUkFNELs"
CANAL_ID = "@promotechbrasil01"

CATEGORIAS = [
    "ssd",
    "placa de video",
    "processador",
    "mouse gamer",
    "teclado mecanico",
    "headset gamer",
    "monitor gamer",
    "notebook gamer"
]

ENVIADOS = []

# =====================================================
# FLASK
# =====================================================

app = Flask(__name__)

@app.route("/")
def home():
    return "BOT PROMOTECH ONLINE"

# =====================================================
# TELEGRAM
# =====================================================

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        data = {
            "chat_id": CANAL_ID,
            "text": msg,
            "parse_mode": "HTML"
        }

        r = requests.post(url, json=data, timeout=20)

        print("TELEGRAM:", r.status_code)

    except Exception as e:
        print("ERRO TELEGRAM:", e)

# =====================================================
# MERCADO LIVRE
# =====================================================

def buscar_produtos(busca):

    try:

        url = (
            "https://api.mercadolibre.com/sites/MLB/search"
            f"?q={busca}&limit=5"
        )

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print("ML STATUS:", r.status_code)

        if r.status_code != 200:
            return []

        data = r.json()

        return data.get("results", [])

    except Exception as e:
        print("ERRO ML:", e)
        return []

# =====================================================
# BOT
# =====================================================

def rodar_bot():

    print("BOT ONLINE")

    enviar_telegram(
        "🤖 <b>PromoTech Bot Online!</b>"
    )

    while True:

        try:

            for categoria in CATEGORIAS:

                print("\nBUSCANDO:", categoria)

                produtos = buscar_produtos(categoria)

                print("ENCONTRADOS:", len(produtos))

                for p in produtos:

                    pid = p.get("id")

                    if pid in ENVIADOS:
                        continue

                    titulo = p.get("title", "Produto")
                    preco = p.get("price", 0)
                    link = p.get("permalink", "")

                    mensagem = (
                        f"🔥 <b>{titulo}</b>\n\n"
                        f"💰 R$ {preco}\n\n"
                        f"🛒 {link}"
                    )

                    enviar_telegram(mensagem)

                    ENVIADOS.append(pid)

                    time.sleep(5)

            print("\nAGUARDANDO NOVO CICLO...\n")

            time.sleep(60)

        except Exception as e:
            print("ERRO LOOP:", e)
            time.sleep(30)

# =====================================================
# THREAD
# =====================================================

threading.Thread(
    target=rodar_bot,
    daemon=True
).start()

# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )