import time
from .config import POLL_INTERVAL
from .collector import BantoBetCollector
from .strategies import process_result
from .telegram_send import send

_last_status = None
_last_result_id = None  # evita processar o mesmo resultado duas vezes


def run():
    global _last_status, _last_result_id

    send("🤖 Bot iniciado com sucesso")

    # Instancia o coletor
    collector = BantoBetCollector()

    while True:
        try:
            # =====================
            # STATUS DA MESA
            # =====================
            status = collector.get_table_status()

            if status != _last_status:
                send(
                    "🟢 BAC BO BANTOBET ABERTO"
                    if status == "OPEN"
                    else "🔴 BAC BO BANTOBET FECHADO"
                )
                _last_status = status

            # =====================
            # RESULTADOS
            # =====================
            if status == "OPEN":
                result = collector.get_last_result()

                # Garante que existe resultado e que não é repetido
                if result and result.get("id") != _last_result_id:
                    messages = process_result(result) or []
                    for msg in messages:
                        send(msg)

                    _last_result_id = result.get("id")

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            # Nunca deixa o bot cair no Railway
            print(f"[BOT ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
