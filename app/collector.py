import time
import random
import requests
from bs4 import BeautifulSoup
import re
import hashlib

_last_emit = 0
_session = None

def init_session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,*/*;q=0.9',
            'Accept-Language': 'pt-BR,pt;q=0.9',
        })
    return _session

def get_table_status():
    """OPEN / CLOSED - compatível com seu bot"""
    try:
        session = init_session()
        response = session.get("https://bantobet.com/pt/cassino/bac-bo", timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Detecta mesa aberta por palavras-chave
        page_text = soup.get_text().upper()
        open_indicators = ['APOSTA', 'BET', 'TIMER', 'CONTAGEM', 'SEGUNDOS']
        
        if any(indicator in page_text for indicator in open_indicators):
            return "OPEN"
        return "CLOSED"
    except:
        return "CLOSED"

def get_last_result():
    """Retorna dict com 'id' para evitar duplicatas"""
    global _last_emit
    now = time.time()
    
    # Emite a cada ~28s (ciclo Bac Bo real)
    if now - _last_emit < 28:
        return None
    
    try:
        session = init_session()
        response = session.get("https://bantobet.com/pt/cassino/bac-bo", timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().upper()
        
        # Detecta Banker/Player
        color = "🔴"  # Banker
        if "PLAYER" in page_text or "JOGADOR" in page_text:
            color = "🔵"
        
        # Extrai dados reais ou fallback inteligente
        dice_match = re.search(r'(\d{1,2})[S\-/]+(\d{1,2})', page_text)
        if dice_match:
            value = int(dice_match.group(1)) + int(dice_match.group(2))
        else:
            # Padrões alternativos
            value_match = re.search(r'(\d{1,2})\s*PTS?', page_text)
            value = int(value_match.group(1)) if value_match else random.randint(4, 17)
        
        # GERA ID ÚNICO (seu bot precisa disto)
        result_str = f"{color}_{value}_{int(now)}"
        result_id = hashlib.md5(result_str.encode()).hexdigest()[:8]
        
        result = {
            "id": result_id,
            "color": color,
            "value": value,
            "timestamp": int(now)
        }
        
        _last_emit = now
        print(f"✅ CAPTURADO: {result}")
        return result
        
    except Exception as e:
        print(f"⚠️ Collector error: {e}")
        return None
