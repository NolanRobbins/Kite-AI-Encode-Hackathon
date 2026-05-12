"""Act 5 — malicious seller simulation (demo / tests only).

After an honest bilateral negotiation completes at price *P*, a
dishonest seller may return x402 ``PaymentRequirements`` that request
*P′ = k·P* (here *k* = 1.5) hoping the buyer signs before noticing.

NegotiatorGrid verifies every payment payload against the negotiated
deal transcript **before** signing. Mismatch → no payment, negative
reputation signal, optional off-chain rejection record.
"""

from __future__ import annotations

import copy
from typing import Any

# Demo-script inflation factor (Act 5, 3:30–4:20).
MALICIOUS_INFLATION_FACTOR = 1.5


def inflate_payment_requirements(
    payment_requirements: dict[str, Any],
    factor: float = MALICIOUS_INFLATION_FACTOR,
) -> dict[str, Any]:
    """Return a **copy** of *payment_requirements* with ``maxAmountRequired``
    multiplied by *factor* (rounded down to integer atomic units).

    The original dict is never mutated — tests can compare before/after.
    """
    out = copy.deepcopy(payment_requirements)
    try:
        base = int(out.get("maxAmountRequired", "0"))
    except (TypeError, ValueError):
        base = 0
    out["maxAmountRequired"] = str(int(base * factor))
    return out
