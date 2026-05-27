cat > promotech_bot.py << 'FIM'
import requests
import json
import time
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES
# ============================================================

TELEGRAM_TOKEN = "8859168984:AAH8nvexWLrbVjGX46cDSfzaCEteUkFNELs"
CANAL_ID = "@promotechbrasil01"

# ID afiliado correto
PUBLISHER_ID = "silvarodri20221029134247"

CATEGORIAS = [
    "ssd",
    "placa de video",
    "rx 7600",
    "rtx 4060",
    "rtx 4070",
    "processador",
    "ryzen",
    "intel i5",
    "intel i7",
    "notebook gamer",
    "monitor gamer",
    "mouse gamer",
    "teclado mecanico",
    "headset gamer",
    "cadeira gamer",
    "gabinete gamer",
    "fonte gamer",
    "water cooler",
    "pc gamer"
]

ARQUIVO = "enviados.json"

# ============================================================
# SESSION REQUESTS
# ============================================================

session = requests.Session()

# ============================================================
# SALVAR ENVIADOS
# ============================================================

def carregar():

    try:

        with open(ARQUIVO, "r") as f:
            return json.load(f)

    except:

        return []

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

def preco(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# ============================================================
# BUSCAR PRODUTOS
# ============================================================

def buscar(termo):

    try:

        url = (
            "https://api.mercadolibre.com/sites/MLB/search"
            f"?q={termo}"
            "&limit=10"
            "&sort=relevance"
        )

        headers = {

            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            ),

            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Connection": "keep-alive"

        }

        response = session.get(

            url,
            headers=headers,
            timeout=30

        )

        print(f"📡 ML status: {response.status_code}")

        if response.status_code != 200:

            print(response.text)

            return []

        dados = response.json()

        produtos = dados.get(
            "results",
            []
        )

        print(
            f"🔍 {termo}: "
            f"{len(produtos)} produtos"
        )

        return produtos

    except Exception as e:

        print(f"❌ ERRO ML: {e}")

        time.sleep(10)

        return []

# ============================================================
# ENVIAR TELEGRAM
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
            "parse_mode": "HTML",
            "disable_web_page_preview": False

        }

        headers = {

            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"

        }

        response = session.post(

            url,
            json=payload,
            headers=headers,
            timeout=30

        )

        print(
            f"📨 Telegram status: "
            f"{response.status_code}"
        )

        if response.status_code == 200:

            return True

        print(response.text)

    except Exception as e:

        print(f"❌ Telegram erro: {e}")

        # espera antes de tentar novamente
        time.sleep(15)

    return False

# ============================================================
# PROCESSAR PRODUTO
# ============================================================

def processar(produto, enviados):

    try:

        produto_id = str(
            produto.get("id", "")
        )

        # evita repetir
        if produto_id in enviados:
            return False

        titulo = produto.get(
            "title",
            ""
        )

        valor = produto.get(
            "price",
            0
        )

        valor_antigo = (
            produto.get("original_price")
            or 0
        )

        permalink = produto.get(
            "permalink",
            ""
        )

        if not permalink:
            return False

        link = afiliado(
            permalink
        )

        desconto = 0

        if valor_antigo > valor:

            desconto = int(
                (
                    (valor_antigo - valor)
                    / valor_antigo
                ) * 100
            )

        # ====================================================

        if desconto > 0:

            mensagem = (

                "🔥 <b>SUPER OFERTA TECH</b>\n\n"

                f"📌 <b>{titulo}</b>\n\n"

                f"💸 De: "
                f"<s>{preco(valor_antigo)}</s>\n"

                f"💰 Por: "
                f"<b>{preco(valor)}</b>\n"

                f"🏷️ "
                f"<b>{desconto}% OFF</b>\n\n"

                f"🛒 "
                f"<a href='{link}'>"
                f"👉 COMPRAR AGORA"
                f"</a>\n\n"

                "#PromoTech #Oferta #Gamer"

            )

        else:

            mensagem = (

                "💻 <b>PRODUTO TECH</b>\n\n"

                f"📌 <b>{titulo}</b>\n\n"

                f"💰 "
                f"<b>{preco(valor)}</b>\n\n"

                f"🛒 "
                f"<a href='{link}'>"
                f"👉 VER PRODUTO"
                f"</a>\n\n"

                "#PromoTech #Tecnologia"

            )

        sucesso = enviar(
            mensagem
        )

        if sucesso:

            enviados.append(
                produto_id
            )

            salvar(enviados)

            print(
                f"✅ {titulo[:60]}"
            )

            return True

    except Exception as e:

        print(
            f"❌ Produto erro: {e}"
        )

    return False

# ============================================================
# LOOP PRINCIPAL
# ============================================================

def executar():

    enviados = carregar()

    enviar(

        "🤖 <b>PromoTech Bot ativado!</b>\n\n"

        "🔥 Monitorando ofertas tech "
        "automaticamente.\n\n"

        "#PromoTech #Automação"

    )

    print("🚀 BOT INICIADO!")

    while True:

        try:

            print(
                f"\n⏰ "
                f"{datetime.now().strftime('%d/%m %H:%M:%S')}"
            )

            for categoria in CATEGORIAS:

                produtos = buscar(
                    categoria
                )

                for produto in produtos:

                    processar(
                        produto,
                        enviados
                    )

                    # evita bloqueio
                    time.sleep(3)

                time.sleep(2)

        except Exception as e:

            print(
                f"❌ ERRO GERAL: {e}"
            )

            time.sleep(15)

# ============================================================
# START
# ============================================================

executar()

FIM