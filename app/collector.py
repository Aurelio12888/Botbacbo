import requests
from bs4 import BeautifulSoup
import re
import time
import hashlib
import logging
from datetime import datetime

# Config logging simples pro Railway
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BantoBetCollector:
    def __init__(self):
        self.url = "https://bantobet.com/pt/cassino/bac-bo"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_table_status(self):
        """Retorna 'OPEN' ou 'CLOSED' baseado no HTML"""
        try:
            response = self.session.get(self.url, timeout=12)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Keywords pra OPEN (apostas ativas)
            open_keywords = ['aposta', 'bet', 'timer', 'tempo', '00:', 'segundos']
            # Keywords pra CLOSED (resultado ou aguardando)
            closed_keywords = ['resultado', 'ganhador', 'winner', 'pago']
            
            text_content = soup.get_text().lower()
            
            if any(keyword in text_content for keyword in open_keywords):
                return "OPEN"
            else:
                return "CLOSED"
                
        except Exception as e:
            logger.error(f"Erro status: {e}")
            return "ERROR"
    
    def get_last_result(self):
        """Extrai último resultado: color + value + timestamp"""
        try:
            response = self.session.get(self.url, timeout=12)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Regex pro resultado: 🔴12 ou 🔵9 ou números com S-
            result_pattern = r'([🔴🔵])?(\d{1,2})[S\-/](\d{1,2})'
            matches = re.findall(result_pattern, soup.get_text())
            
            if not matches:
                return None
            
            # Pega o último resultado válido (4-17 pontos)
            for match in reversed(matches):
                color, dice1, dice2 = match
                value = int(dice1) + int(dice2)
                
                if 4 <= value <= 17:
                    color = color if color else "🔴"  # Default Banker
                    timestamp = int(time.time())
                    
                    # Gera ID único pra evitar duplicatas
                    result_id = hashlib.md5(f"{color}_{value}_{timestamp}".encode()).hexdigest()[:8]
                    
                    return {
                        "id": result_id,
                        "color": color,
                        "value": value,
                        "timestamp": timestamp
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro resultado: {e}")
            return None

def main():
    """Loop principal - roda pra sempre"""
    collector = BantoBetCollector()
    
    while True:
        try:
            # Checa status a cada 28s (ritmo Bac Bo)
            status = collector.get_table_status()
            logger.info(f"Status: {status}")
            
            if status == "OPEN":
                logger.info("📊 Mesa ABERTA - aguardando resultado...")
            elif status == "CLOSED":
                result = collector.get_last_result()
                if result:
                    logger.info(f"✅ CAPTURADO: {result}")
                    # Aqui você chama process_result() se tiver
                    # process_result(result)
                else:
                    logger.info("❌ Sem resultado novo")
            
            time.sleep(28)  # Ciclo Bac Bo
            
        except KeyboardInterrupt:
            logger.info("Parando collector...")
            break
        except Exception as e:
            logger.error(f"Erro loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
