
import requests
import json
import time
import hashlib
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES - EDITE AQUI
# ============================================================
TELEGRAM_TOKEN = "8859168984:AAH8nvexWLrbVjGX46cDSfzaCEteUkFNELs"
CANAL_ID = "@promotechbrasil01"
PUBLISHER_ID = "XHKT38-E62C"

# Categorias de tecnologia para buscar no ML
CATEGORIAS = [
    "SSD",
    "placa de video",
    "processador",
    "notebook gamer",
    "teclado mecanico",
    "mouse gamer",
    "monitor gamer",
    "memoria ram",
    "headset gamer",
    "gabinete pc"
]

# Arquivo para controlar produtos já enviados
ARQUIVO_ENVIADOS = "produtos_enviados.json"

# ============================================================
# FUNÇÕES
# ============================================================

def carregar_enviados():
    try:
        with open(ARQUIVO_ENVIADOS, "r") as f:
            return json.load(f)
    except:
        return []

def salvar_enviados(lista):
    with open(ARQUIVO_ENVIADOS, "w") as f:
        json.dump(lista[-500:], f)  # Guarda últimos 500

def gerar_link_afiliado(url_produto):
    """Gera link com ID de afiliado do ML"""
    if "?" in url_produto:
        return f"{url_produto}&matt_tool={PUBLISHER_ID}&matt_word=&matt_source=telegram"
    else:
        return f"{url_produto}?matt_tool={PUBLISHER_ID}&matt_word=&matt_source=telegram"

def buscar_produtos_ml(termo):
    """Busca produtos em promoção no ML"""
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&sort=price_asc&condition=new&limit=3"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            return dados.get("results", [])
    except Exception as e:
        print(f"Erro ao buscar {termo}: {e}")
    return []

def formatar_preco(preco):
    """Formata preço em reais"""
    return f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def enviar_telegram(mensagem):
    """Envia mensagem pro canal do Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dados = {
        "chat_id": CANAL_ID,
        "text": mensagem,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=dados, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")
        return False

def processar_produto(produto, enviados):
    """Processa e envia um produto se ainda não foi enviado"""
    produto_id = str(produto.get("id", ""))
    
    if produto_id in enviados:
        return False
    
    titulo = produto.get("title", "")
    preco = produto.get("price", 0)
    preco_original = produto.get("original_price", 0)
    link = produto.get("permalink", "")
    vendedor = produto.get("seller", {}).get("nickname", "")
    
    # Só posta se tiver desconto real
    if preco_original and preco_original > preco:
        desconto = int(((preco_original - preco) / preco_original) * 100)
        if desconto < 5:  # Ignora descontos menores que 5%
            return False
    else:
        desconto = 0
    
    link_afiliado = gerar_link_afiliado(link)
    
    # Monta a mensagem
    if desconto > 0:
        mensagem = (
            f"🔥 <b>OFERTA IMPERDÍVEL!</b>\n\n"
            f"📌 {titulo}\n\n"
            f"💰 <s>{formatar_preco(preco_original)}</s> → <b>{formatar_preco(preco)}</b>\n"
            f"🏷️ <b>{desconto}% OFF</b>\n\n"
            f"🛒 <a href='{link_afiliado}'>COMPRAR AGORA</a>\n\n"
            f"#PromoTech #Ofertas #MercadoLivre #Gamer"
        )
    else:
        mensagem = (
            f"💻 <b>PRODUTO EM DESTAQUE!</b>\n\n"
            f"📌 {titulo}\n\n"
            f"💰 <b>{formatar_preco(preco)}</b>\n\n"
            f"🛒 <a href='{link_afiliado}'>VER PRODUTO</a>\n\n"
            f"#PromoTech #MercadoLivre #Gamer"
        )
    
    sucesso = enviar_telegram(mensagem)
    
    if sucesso:
        enviados.append(produto_id)
        print(f"✅ Enviado: {titulo[:50]}...")
        return True
    
    return False

def executar_ciclo():
    """Executa um ciclo de busca e envio"""
    print(f"\n⏰ Iniciando ciclo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    enviados = carregar_enviados()
    total_enviados = 0
    
    for categoria in CATEGORIAS:
        print(f"🔍 Buscando: {categoria}")
        produtos = buscar_produtos_ml(categoria)
        
        for produto in produtos:
            if processar_produto(produto, enviados):
                total_enviados += 1
                time.sleep(3)  # Pausa entre envios
            
            if total_enviados >= 5:  # Máximo 5 produtos por ciclo
                break
        
        if total_enviados >= 5:
            break
        
        time.sleep(2)
    
    salvar_enviados(enviados)
    print(f"✅ Ciclo finalizado. {total_enviados} produtos enviados.")

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("🚀 PromoTech Bot iniciado!")
    print(f"📢 Canal: {CANAL_ID}")
    print(f"🔄 Buscando a cada 1 hora...\n")
    
    # Envia mensagem de início
    enviar_telegram(
        "🤖 <b>PromoTech Bot ativado!</b>\n\n"
        "🔥 Agora você receberá as melhores ofertas de tecnologia automaticamente!\n\n"
        "#PromoTech #Automação"
    )
    
    while True:
        try:
            executar_ciclo()
        except Exception as e:
            print(f"❌ Erro no ciclo: {e}")
        
        print("⏳ Aguardando 1 hora para próximo ciclo...")
        time.sleep(3600)  # Espera 1 hora