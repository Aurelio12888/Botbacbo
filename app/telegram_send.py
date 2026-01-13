from telegram import Bot
from .config import TOKEN, CHAT_ID

_bot = None

def _get_bot():
    global _bot
    if _bot is None:
        _bot = Bot(token=TOKEN)
    return _bot

def send(text):
    if not TOKEN or not CHAT_ID:
        raise RuntimeError("TOKEN ou CHAT_ID não definidos no Railway")
    _get_bot().send_message(chat_id=CHAT_ID, text=text)
