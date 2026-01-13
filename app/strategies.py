from .config import CONFIDENCE, MAX_GALES

# =====================
# ESTADO GLOBAL
# =====================
history = []
current_entry = None
current_gale = 0
current_strategy = None


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
    if len(history) < 3:
        return None
    if history[-1] == history[-2] == history[-3]:
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
# MOTOR PRINCIPAL
# =====================

def check_strategies():
    for strat in (
        zig_zag,
        tendencia,
        reversao,
        quebra_tendencia,
        consolidacao,
    ):
        result = strat()
        if result:
            return result
    return None


def process_result(result):
    global current_entry, current_gale, current_strategy

    add_history(result)
    messages = []

    # Procurar novo sinal
    if current_entry is None:
        decision = check_strategies()
        if not decision:
            return []

        current_entry, current_strategy = decision
        current_gale = 0

        messages.append(
            f"""🎲 BAC BO – SINAL CONFIRMADO
📊 Estratégia: {current_strategy}
📊 Confiança: {CONFIDENCE}%
👉 ENTRADA: {current_entry}
♻️ Até {MAX_GALES} GALES
"""
        )
        return messages

    # WIN
    if result["color"] == current_entry:
        messages.append(
            f"""✅ WIN
📊 Estratégia: {current_strategy}
Resultado: {result['color']}{result['value']}
Confiança: {CONFIDENCE}%
"""
        )
        current_entry = None
        current_gale = 0
        current_strategy = None
        return messages

    #
