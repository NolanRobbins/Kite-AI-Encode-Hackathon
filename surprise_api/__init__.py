"""Surprise API — a standalone x402-gated FastAPI service.

This is the Day-4 "wow moment" seller. It runs as its **own process**
(not inside NegotiatorGrid's backend) so the buyer agent genuinely
discovers it over MCP, verifies its identity on ERC-8004, negotiates a
price, pays via x402, and only then gets data. No code path lets the
buyer skip the negotiation or the payment — you have to walk the real
chain every time.

Why "surprise"? In the demo, the judge watches the buyer agent meet a
service it's never seen before (an instance of this process), go
through the full discover → verify → negotiate → pay → consume loop
in under 10 seconds, and render live weather/NVDA data. That's the
first clearly-autonomous interaction in the video.

Key design choices:

* **Hand-rolled x402 middleware** — not the `fast-x402` PyPI package.
  Kite compatibility is hand-tuned (EIP-712 matches our `X402Settler`)
  and we avoid pulling unvetted community code mid-hackathon.
* **Wired into the existing DiscoveryService** — starting the process
  registers a ``ServiceRecord`` in the same :class:`LocalRegistry` the
  backend uses, so the live discovery chain actually surfaces it.
* **Demo-safe data** — real live weather uses open-meteo (no key
  required). If open-meteo is unreachable, we fall back to a
  deterministic scripted payload so the demo never dies on a network
  blip.
"""

from surprise_api.app import SURPRISE_API_SERVICE_RECORD, build_app

__all__ = ["build_app", "SURPRISE_API_SERVICE_RECORD"]
