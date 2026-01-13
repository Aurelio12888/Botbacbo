from .config import CONFIDENCE, MAX_GALES

# =====================
# ESTADO GLOBAL
# =====================
history = []
current_entry = None
current_gale = 0
current_strategy = None
signal_active = False
last_strategy_used = None  # evita repetir a mesma estratégia em sequência

STRATEGY_LABELS = {
    "ZIG-ZAG": "🔁 ZIG-ZAG",
    "TENDÊNCIA": "📈 TENDÊNCIA",
    "REVERSÃO": "🔄 REVERSÃO",
    "QUEBRA DE TENDÊNCIA": "💥 QUEBRA DE TENDÊNCIA",
    "CONSOLIDAÇÃO": "🧱 CONSOLIDAÇÃO",
}

# =====================
# HISTÓRICO
# =====================
def add_history(result):
    history.append(result["color"])
    if len(history) > 10:
        history.pop(0)

# =====================
# ESTRATÉGIAS
# =====================
def zig_zag():
    if len(history) < 4:
        return None
    a, b, c, d = history[-4:]
    if a != b and b != c and c != d and a == c and b == d:
        return history[-1], "ZIG-ZAG"
    return None

def tendencia():
    # Tornar mais exigente: precisa de 4 iguais seguidos
    if len(history) < 4:
        return None
    if history[-1] == history[-2] == history[-3] == history[-4]:
        return history[-1], "TENDÊNCIA"
    return None

def reversao():
    if len(history) < 2:
        return None
    if history[-1] == history[-2]:
        entrada = "🔵" if history[-1] == "🔴" else "🔴"
        return entrada, "REVERSÃO"
    return None

def quebra_tendencia():
    if len(history) < 4:
        return None
    if history[-4] == history[-3] == history[-2] and history[-1] != history[-2]:
        return history[-1], "QUEBRA DE TENDÊNCIA"
    return None

def consolidacao():
    if len(history) < 4:
        return None
    a, b, c, d = history[-4:]
    if a == b and c == d and a != c:
        return d, "CONSOLIDAÇÃO"
    return None

# =====================
# MOTOR DE DECISÃO
# =====================
def check_strategies():
    global last_strategy_used
    # Mudamos a ordem para não priorizar sempre tendência
    for strat in (zig_zag, reversao, quebra_tendencia, consolidacao, tendencia):
        result = strat()
        if result and result[1] != last_strategy_used:
            last_strategy_used = result[1]
            return result
    return None

# =====================
# PROCESSAMENTO PRINCIPAL
# =====================
def process_result(result):
    global current_entry, current_gale, current_strategy, signal_active

    messages = []
    add_history(result)

    last_sequence = " ".join(history[-5:])

    # =====================
    # NOVO SINAL
    # =====================
    if not signal_active:
        decision = check_strategies()
        if not decision:
            return messages

        current_entry, current_strategy = decision
        current_gale = 0
        signal_active = True
        strategy_name = STRATEGY_LABELS.get(current_strategy, current_strategy)

        messages.append(
            f"""🎲 BAC BO – SINAL CONFIRMADO
📊 Estratégia: {strategy_name}
📈 Histórico: {last_sequence}
📊 Confiança: {CONFIDENCE}%
👉 ENTRADA: {current_entry}
♻️ Até {MAX_GALES} GALES
"""
        )
        return messages

    strategy_name = STRATEGY_LABELS.get(current_strategy, current_strategy)

    # =====================
    # WIN
    # =====================
    if result["color"] == current_entry:
        messages.append(
            f"""✅ WIN
📊 Estratégia: {strategy_name}
📈 Histórico: {last_sequence}
Resultado: {result['color']}{result['value']}
Confiança: {CONFIDENCE}%
"""
        )
        # reset
        current_entry = None
        current_gale = 0
        current_strategy = None
        signal_active = False
        return messages

    # =====================
    # GALE
    # =====================
    current_gale += 1

    if current_gale <= MAX_GALES:
        messages.append(
            f"""⚠️ GALE {current_gale}
📊 Estratégia: {strategy_name}
📈 Histórico: {last_sequence}
Mantém entrada: {current_entry}
"""
        )
        return messages

    # =====================
    # LOSS
    # =====================
    messages.append(
        f"""❌ LOSS
📊 Estratégia: {strategy_name}
📈 Histórico: {last_sequence}
Resultado: {result['color']}{result['value']}
"""
    )

    # reset
    current_entry = None
    current_gale = 0
    current_strategy = None
    signal_active = False
    return messages


