import requests
import json
import time

# CONFIGURAÇÕES - MUDE AQUI
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"  # MUDE ISSO!
CANAL_ID = "@promotechbrasil01"
PUBLISHER_ID = "XHKT38-E62C"

# Categorias
CATEGORIAS = ["SSD", "placa de video", "processador", "notebook gamer"]

ARQUIVO_ENVIADOS = "enviados.json"

def carregar_enviados():
    try:
        with open(ARQUIVO_ENVIADOS, "r") as f:
            return json.load(f)
    except:
        return []

def salvar_enviados(lista):
    with open(ARQUIVO_ENVIADOS, "w") as f:
        json.dump(lista[-200:], f)

def buscar_produtos(termo):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&sort=price_asc&limit=3"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r.json().get("results", [])
    except:
        return []
    return []

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dados = {"chat_id": CANAL_ID, "text": texto, "parse_mode": "HTML"}
    try:
        requests.post(url, json=dados, timeout=10)
        return True
    except:
        return False

# Loop principal
print("Bot iniciado!")
enviados = carregar_enviados()

while True:
    for categoria in CATEGORIAS:
        produtos = buscar_produtos(categoria)
        
        for p in produtos:
            id_produto = str(p.get("id", ""))
            
            if id_produto not in enviados:
                titulo = p.get("title", "")
                preco = p.get("price", 0)
                link = p.get("permalink", "")
                
                # Link afiliado
                link_afiliado = f"{link}?matt_tool={PUBLISHER_ID}"
                
                msg = f"🔥 {titulo}\n💰 R$ {preco}\n🛒 {link_afiliado}"
                
                if enviar_mensagem(msg):
                    enviados.append(id_produto)
                    salvar_enviados(enviados)
                    print(f"Enviado: {titulo[:30]}")
                    time.sleep(5)
        
        time.sleep(10)
    
    print("Esperando 30 min...")
    time.sleep(1800)  # 30 minutos
