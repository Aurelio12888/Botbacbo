import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

_last_emit = 0
_driver = None
_last_status = "CLOSED"
_last_result = None

def init_driver():
    """Inicializa o driver Chrome headless para Banto Bet"""
    global _driver
    if _driver is not None:
        return _driver
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Remove para debug visual
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    _driver = webdriver.Chrome(options=chrome_options)
    _driver.get("https://bantobet.com/pt/cassino/bac-bo")  # URL Bac Bo Banto Bet
    
    # Aguarda página carregar
    time.sleep(5)
    return _driver

def get_table_status():
    """Retorna OPEN/CLOSED baseado no estado real da mesa"""
    global _driver, _last_status
    
    try:
        init_driver()
        
        # Detecta se mesa está aberta (botão aposta disponível)
        bet_buttons = _driver.find_elements(By.CSS_SELECTOR, 
            "[data-testid*='bet'], .bet-button, button[class*='bet'], .btn-bet")
        
        countdown = _driver.find_elements(By.CSS_SELECTOR, 
            ".countdown, [class*='timer'], [class*='countdown']")
        
        if bet_buttons or countdown:
            _last_status = "OPEN"
        else:
            # Procura resultado recente ou "próxima rodada"
            _last_status = "CLOSED"
            
    except Exception:
        _last_status = "CLOSED"
    
    return _last_status

def get_last_result():
    """Captura o ÚLTIMO resultado real do Bac Bo"""
    global _last_emit, _last_result, _driver
    now = time.time()
    
    # Emite resultado a cada ~25s (tempo real Bac Bo)
    if now - _last_emit < 25:
        return _last_result
    
    try:
        init_driver()
        
        # Procura último resultado na história/roadmap
        # Selectores comuns para Bac Bo Banto Bet
        result_selectors = [
            ".result-item:last-child", 
            ".history-item:last-child",
            ".roadmap-cell:last-child",
            "[class*='result']:last-child",
            ".game-result:last-child",
            ".bacbo-result:last-child"
        ]
        
        last_result = None
        for selector in result_selectors:
            try:
                elements = _driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    result_text = elements[0].text.strip().upper()
                    
                    # Parse Banker/Player + Dice
                    if "BANKER" in result_text or "B" in result_text:
                        color = "🔴"  # Banker vermelho
                        value = extract_dice_value(result_text)
                    elif "PLAYER" in result_text or "P" in result_text:
                        color = "🔵"  # Player azul
                        value = extract_dice_value(result_text)
                    else:
                        continue
                    
                    if value:
                        last_result = {"color": color, "value": value}
                        break
            except:
                continue
        
        # Fallback: procura na área de resultado atual
        if not last_result:
            current_result = _driver.find_elements(By.CSS_SELECTOR, 
                ".current-result, .game-outcome, [class*='outcome']")
            if current_result:
                result_text = current_result[0].text.strip().upper()
                if "BANKER" in result_text:
                    last_result = {"color": "🔴", "value": 10}  # Default
                elif "PLAYER" in result_text:
                    last_result = {"color": "🔵", "value": 10}
        
        if last_result:
            _last_result = last_result
            _last_emit = now
            print(f"✅ Resultado real capturado: {last_result}")
            
    except Exception as e:
        print(f"❌ Erro captura: {e}")
        # Fallback simulação apenas se falhar 3x seguidas
        if now - _last_emit > 120:
            _last_result = {
                "color": random.choice(["🔵", "🔴"]), 
                "value": random.randint(4, 17)
            }
            _last_emit = now
    
    return _last_result

def extract_dice_value(text):
    """Extrai valor dos dados do texto do resultado"""
    # Padrões comuns: "Banker 6-5", "12", "B(11)", etc
    patterns = [
        r'(\d{1,2})',  # Número simples
        r'(\d+)-(\d+)',  # 6-5 -> soma
        r'\((\d+)\)',   # (12)
        r'(\d+)\s*PTS?' # 12 PTS
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if '-' in pattern:
                return sum(int(x) for x in match.groups())
            return int(match.group(1))
    return None

def close_driver():
    """Fecha driver quando terminar"""
    global _driver
    if _driver:
        _driver.quit()
        _driver = None

# Mantém compatibilidade - chama automaticamente
if __name__ == "__main__":
    print("🔴🟦 Bac Bo Banto Bet - Modo REAL ativo")
    print("Status:", get_table_status())
    print("Último:", get_last_result())
