import os

# =====================
# VARIÁVEIS DE AMBIENTE (Railway)
# =====================
TOKEN = os.getenv("TOKEN")      # Token do bot do Telegram
CHAT_ID = os.getenv("CHAT_ID")  # ID do chat ou canal

# =====================
# CONFIGURAÇÕES GERAIS
# =====================
# Intervalo curto para não atrasar sinais
POLL_INTERVAL = 5        # segundos entre cada checagem

# Controle de estratégia
MAX_GALES = 2            # número máximo de gales permitidos
CONFIDENCE = 96          # nível de confiança exibido nas mensagens (%)

# =====================
# REGRAS DE SINAL
# =====================
# O bot só envia sinal quando:
# 1. A estratégia for confirmada
# 2. A rodada estiver aberta
# 3. Ainda não tiver sinal ativo na rodada
# 4. O sinal anterior já tiver sido resolvido (WIN ou LOSS)
