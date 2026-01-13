# Collector placeholder. Replace internals to connect to real Bantobet data.
# Must return table status and last result when available.

import time
import random

_last_emit = 0

def get_table_status():
    # OPEN / CLOSED (placeholder)
    return "OPEN"

def get_last_result():
    # Simulate one result every ~10s
    global _last_emit
    now = time.time()
    if now - _last_emit < 10:
        return None
    _last_emit = now

    color = random.choice(["🔵", "🔴"])
    value = random.randint(4, 17)
    return {"color": color, "value": value}
