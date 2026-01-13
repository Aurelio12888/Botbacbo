import requests
import re
import time
import hashlib
import logging
from datetime import datetime

# Seus requirements: requests + urllib3 + six já inclusos
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
        self.last_result_id = None
        
    def get_table_status(self):
        """Detecta OPEN/CLOSED só com requests + regex"""
        try:
            response = self.session.get(self.url, timeout=12)
            text = response.text.lower()
            
            # Keywords OPEN (apostas ativas)
            if re.search(r'aposta|bet|timer|tempo|00:|segundos|\d{2}:\d{2}', text):
                return "OPEN"
            # Keywords CLOSED (resultado)
            elif re.search(r'resultado|ganhador|winner|pago|parabéns', text):
                return "CLOSED"
            else:
                return "UNKNOWN"
                
        except Exception as e:
            logger.error(f"Erro status: {e}")
            return "ERROR"
    
    def get_last_result(self):
        """Extrai resultado com regex puro"""
        try:
            response = self.session.get(self.url, timeout=12)
            text = response.text
            
            # Regex otimizado pro Bac Bo Banto Bet
            patterns = [
                r'([🔴🔵]?)(\d{1,2})[S\-/](\d{1,2})',  # 🔴12S9 ou 12-9
                r'([🔴🔵]?)(\d+)(\s*[-/S]\s*)(\d+)',    # 🔴 12 - 9
                r'([🔴🔵])\s*(\d{1,2})\s*[-/S]\s*(\d{1,2})'  # 🔴 12 S 9
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    for match in reversed(matches):  # Último resultado
                        color, dice1, sep, dice2 = match if len(match) == 4 else (*match, '')
                        try:
                            value = int(dice1) + int(dice2)
                            if 4 <= value <= 17:  # Bac Bo válido
                                color = color if color else "🔴"
                                timestamp = int(time.time())
                                
                                # ID único anti-duplicata
                                result_id = hashlib.md5(f"{color}_{value}_{timestamp}".encode()).hexdigest()[:8]
                                
                                result = {
                                    "id": result_id,
                                    "color": color,
                                    "value": value,
                                    "timestamp": timestamp
                                }
                                
                                # Evita duplicatas
                                if result_id != self.last_result_id:
                                    self.last_result_id = result_id
                                    return result
                        except (ValueError, IndexError):
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Erro resultado: {e}")
            return None

def main():
    """Loop principal standalone"""
    collector = BantoBetCollector()
    logger.info("🚀 Banto Bet Collector iniciado!")
    
    while True:
        try:
            status = collector.get_table_status()
            logger.info(f"Status: {status}")
            
            if status == "OPEN":
                logger.info("📊 Mesa ABERTA - aguardando...")
            elif status == "CLOSED":
                result = collector.get_last_result()
                if result:
                    logger.info(f"✅ CAPTURADO: {result}")
                    # Aqui você integra seu telegram_send:
                    # telegram_send.send(result)
                else:
                    logger.info("❌ Sem resultado novo")
            
            time.sleep(28)  # Ciclo Bac Bo
            
        except KeyboardInterrupt:
            logger.info("🛑 Collector parado")
            break
        except Exception as e:
            logger.error(f"Erro loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
