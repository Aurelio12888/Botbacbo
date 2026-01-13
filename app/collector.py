import requests
import re
import time
import hashlib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class BantoBetCollector:
    def __init__(self):
        self.url = "https://bantobet.com/pt/cassino/bac-bo"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 '
                          'Mobile/15E148 Safari/604.1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_result_id = None

    def get_table_status(self):
        """Detecta OPEN/CLOSED com base em palavras-chave"""
        try:
            response = self.session.get(self.url, timeout=12)
            text = response.text.lower()

            if re.search(r'aposta|bet|timer|tempo|00:|segundos|\d{2}:\d{2}', text):
                return "OPEN"
            elif re.search(r'resultado|ganhador|winner|pago|parabéns', text):
                return "CLOSED"
            else:
                return "UNKNOWN"

        except Exception as e:
            logger.error(f"Erro status: {e}")
            return "ERROR"

    def get_last_result(self):
        """Extrai último resultado do Bac Bo com regex mais específico"""
        try:
            response = self.session.get(self.url, timeout=12)
            text = response.text

            # Regex ajustado para capturar resultados em spans ou blocos
            match = re.findall(r'class="result (red|blue)">(\d+)<', text)
            if match and len(match) >= 2:
                color_map = {"red": "🔴", "blue": "🔵"}
                # pega os dois últimos números (dados)
                dice1 = int(match[-2][1])
                dice2 = int(match[-1][1])
                color = color_map.get(match[-1][0], "🔴")
                value = dice1 + dice2

                result_id = hashlib.md5(f"{color}_{value}".encode()).hexdigest()[:8]
                if result_id != self.last_result_id:
                    self.last_result_id = result_id
                    return {
                        "id": result_id,
                        "color": color,
                        "value": value,
                        "timestamp": int(time.time())
                    }
            return None

        except Exception as e:
            logger.error(f"Erro resultado: {e}")
            return None
