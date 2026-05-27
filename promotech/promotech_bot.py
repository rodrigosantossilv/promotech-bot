import requests
import time
import threading
from flask import Flask

# =====================================================
# CONFIG
# =====================================================
TELEGRAM_TOKEN = "8859168984:AAH8nvexWLrbVjGX46cDSfzaCEteUkFNELs"
CANAL_ID = "@promotechbrasil01"
PUBLISHER_ID = "XHKT38-E62C"

CATEGORIAS = [
    "ssd",
    "placa de video",
    "processador",
    "mouse gamer",
    "teclado mecanico",
    "headset gamer",
    "monitor gamer",
    "notebook gamer",
    "memoria ram",
    "cadeira gamer",
    "gabinete pc",
    "cooler cpu",
    "fonte atx",
    "webcam",
    "microfone"
]

ENVIADOS = []

# =====================================================
# FLASK - Mantém o servidor online
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
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        r = requests.post(url, json=data, timeout=20)
        print("TELEGRAM:", r.status_code)
    except Exception as e:
        print("ERRO TELEGRAM:", e)

# =====================================================
# MERCADO LIVRE
# =====================================================
def gerar_link_afiliado(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}matt_tool={PUBLISHER_ID}&matt_source=telegram&matt_word=promotech"

def formatar_preco(preco):
    return f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def buscar_produtos(busca):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={busca}&limit=10&sort=relevance&condition=new"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        print(f"ML [{busca}]: {r.status_code}")
        if r.status_code != 200:
            return []
        return r.json().get("results", [])
    except Exception as e:
        print("ERRO ML:", e)
        return []

# =====================================================
# BOT PRINCIPAL
# =====================================================
def rodar_bot():
    print("BOT ONLINE")
    enviar_telegram("🤖 <b>PromoTech Bot Online!</b>\n\n🔥 Buscando as melhores ofertas de tecnologia!\n\n#PromoTech #Automação")

    while True:
        try:
            total = 0
            for categoria in CATEGORIAS:
                print(f"\nBUSCANDO: {categoria}")
                produtos = buscar_produtos(categoria)
                print(f"ENCONTRADOS: {len(produtos)}")

                for p in produtos:
                    pid = p.get("id")
                    if pid in ENVIADOS:
                        continue

                    titulo = p.get("title", "Produto")
                    preco = p.get("price", 0)
                    preco_orig = p.get("original_price") or 0
                    link = gerar_link_afiliado(p.get("permalink", ""))

                    # Com desconto
                    if preco_orig and preco_orig > preco:
                        desc = int(((preco_orig - preco) / preco_orig) * 100)
                        mensagem = (
                            f"🔥 <b>OFERTA IMPERDÍVEL!</b>\n\n"
                            f"📌 <b>{titulo}</b>\n\n"
                            f"💰 <s>{formatar_preco(preco_orig)}</s> → <b>{formatar_preco(preco)}</b>\n"
                            f"🏷️ <b>{desc}% OFF</b>\n\n"
                            f"🛒 <a href='{link}'>👉 COMPRAR AGORA</a>\n\n"
                            f"#PromoTech #Ofertas #MercadoLivre #Gamer"
                        )
                    else:
                        # Sem desconto - posta mesmo assim
                        mensagem = (
                            f"💻 <b>PRODUTO EM DESTAQUE!</b>\n\n"
                            f"📌 <b>{titulo}</b>\n\n"
                            f"💰 <b>{formatar_preco(preco)}</b>\n\n"
                            f"🛒 <a href='{link}'>👉 VER PRODUTO</a>\n\n"
                            f"#PromoTech #MercadoLivre #Gamer"
                        )

                    enviar_telegram(mensagem)
                    ENVIADOS.append(pid)
                    total += 1
                    time.sleep(5)

                    if total >= 3:
                        break

                if total >= 3:
                    break

            print(f"\n✅ {total} produtos enviados. Aguardando 1 hora...\n")
            time.sleep(3600)

        except Exception as e:
            print("ERRO LOOP:", e)
            time.sleep(30)

# =====================================================
# THREAD + START
# =====================================================
threading.Thread(target=rodar_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
