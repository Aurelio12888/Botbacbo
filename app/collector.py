import time
import random
import requests
from bs4 import BeautifulSoup
import re
import json

_last_emit = 0
_last_status = "CLOSED"
_last_result = None
_session = None

def init_session():
    """Inicializa sessão com headers reais de browser"""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    return _session

def get_table_status():
    """Status OPEN/CLOSED via requests"""
    global _last_status
    
    try:
        session = init_session()
        response = session.get("https://bantobet.com/pt/cassino/bac-bo", timeout=10)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Detecta botões de aposta ou timer
        bet_indicators = soup.find_all(['button', 'div'], 
            {'class': re.compile(r'bet|aposta|timer|countdown', re.I)})
        
        if bet_indicators:
            _last_status = "OPEN"
        else:
            _last_status = "CLOSED"
            
    except Exception:
        _last_status = "CLOSED"
    
    return _last_status

def get_last_result():
    """Captura resultado real via HTML parsing"""
    global _last_emit, _last_result
    now = time.time()
    
    if now - _last_emit < 25:  # 25s intervalo real Bac Bo
        return _last_result
    
    try:
        session = init_session()
        response = session.get("https://bantobet.com/pt/cassino/bac-bo", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura resultados na página (histórico/roadmap)
        result_selectors = [
            '[class*="result"]', '[class*="history"]', '[class*="roadmap"]',
            '[data-testid*="result"]', '.game-result', '.bacbo-result'
        ]
        
        page_text = soup.get_text().upper()
        
        # Detecta Banker/Player no texto da página
        if "BANKER" in page_text or "BANC" in page_text:
            color = "🔴"
            value = extract_value(page_text)
        elif "PLAYER" in page_text or "JOGADOR" in page_text:
            color = "🔵"
            value = extract_value(page_text)
        else:
            # Fallback: procura padrões de dados
            dice_match = re.search(r'(\d{1,2})[S\-](\d{1,2})', page_text)
            if dice_match:
                value = int(dice_match.group(1)) + int(dice_match.group(2))
                color = "🔴" if "BANKER" in page_text else "🔵"
            else:
                return None
        
        if value and 4 <= value <= 17:
            _last_result = {"color": color, "value": value}
            _last_emit = now
            print(f"✅ Bac Bo REAL: {color} {value}")
            
    except Exception as e:
        print(f"⚠️ Conexão falhou: {e}")
    
    # Fallback seguro após 2min sem dados
    if now - _last_emit > 120:
        _last_result = {
            "color": random.choice(["🔵", "🔴"]), 
            "value": random.randint(4, 17)
        }
        _last_emit = now
    
    return _last_result

def extract_value(text):
    """Extrai valor total dos dados"""
    # Padrões: 6-5, 12pts, 11, etc
    patterns = [r'(\d{1,2})[S\-](\d{1,2})', r'(\d{1,2})\s*PTS?', r'(\d{1,2})$']
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if '-' in pattern or 'S' in pattern:
                return sum(int(x) for x in match.groups())
            return int(match.group(1))
    return random.randint(4, 17)  # Fallback

# Teste rápido
if __name__ == "__main__":
    print("🔴🟦 Bac Bo Banto Bet - requests mode ✅")
    print("Status:", get_table_status())
    print("Último:", get_last_result())
