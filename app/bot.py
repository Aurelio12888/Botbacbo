import time
from .config import POLL_INTERVAL
from .collector import get_table_status, get_last_result
from .strategies import process_result
from .telegram_send import send

_last_status = None

def run():
    global _last_status
    while True:
        status = get_table_status()
        if status != _last_status:
            send("🟢 BAC BO BANTOBET ABERTO" if status == "OPEN" else "🔴 BAC BO BANTOBET FECHADO")
            _last_status = status

        if status == "OPEN":
            result = get_last_result()
            if result:
                for msg in process_result(result):
                    send(msg)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
