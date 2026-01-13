import time
from .config import POLL_INTERVAL
from .collector import BantoBetCollector
from .strategies import process_result
from .telegram_send import send

_last_status = None
_last_result_id = None


def run():
    global _last_status, _last_result_id

    send("🤖 Bot iniciado com sucesso")

    collector = BantoBetCollector()

    while True:
        try:
            # Verifica status da mesa
            status = collector.get_table_status()

            if status != _last_status:
                send(
                    "🟢 BAC BO BANTOBET ABERTO"
                    if status == "OPEN"
                    else "🔴 BAC BO BANTOBET FECHADO"
                )
                _last_status = status

            # Se mesa estiver aberta, analisa resultado
            if status == "OPEN":
                result = collector.get_last_result()

                if result and result.get("id") != _last_result_id:
                    # Processa resultado e só envia se houver mensagens relevantes
                    messages = process_result(result) or []
                    if messages:
                        for msg in messages:
                            send(msg)

                    _last_result_id = result.get("id")

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            print(f"[BOT ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
