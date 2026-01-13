import time
from .config import POLL_INTERVAL
from .collector import BantoBetCollector
from .strategies import process_result
from .telegram_send import send

_last_status = None
_last_result_id = None
_signal_sent = False  # controla envio por rodada


def run():
    global _last_status, _last_result_id, _signal_sent

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

                # Reset do controle de sinal ao fechar rodada
                if status == "CLOSED":
                    _signal_sent = False

            # Se mesa estiver aberta, analisa resultado
            if status == "OPEN":
                result = collector.get_last_result()

                if result and result.get("id") != _last_result_id:
                    messages = process_result(result) or []

                    # Só envia se houver estratégia comprovada e ainda não enviou nessa rodada
                    if messages and not _signal_sent:
                        for msg in messages:
                            send(msg)

                        _signal_sent = True
                        _last_result_id = result.get("id")

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            print(f"[BOT ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
