"""Reputation-conditioned negotiation strategy."""

from __future__ import annotations

import logging
import time
from typing import Any

from negotiatorgrid.contracts.reputation_client import ReputationClient
from negotiatorgrid.contracts.deal_record import DealRecordClient
from negotiatorgrid.core.types import AgentProfile  # Pydantic model

logger = logging.getLogger(__name__)

# Cache TTL in seconds.
_CACHE_TTL = 300  # 5 minutes


class ReputationFeed:
    """Reads on-chain reputation data and maps it to negotiation strategies.

    Results are cached for 5 minutes to avoid excessive RPC calls.
    """

    def __init__(
        self,
        reputation_client: ReputationClient,
        deal_record_client: DealRecordClient,
    ) -> None:
        self._reputation = reputation_client
        self._deals = deal_record_client
        self._cache: dict[str, tuple[float, AgentProfile]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_agent_reputation(self, agent_id_or_address: int | str) -> AgentProfile:
        """Fetch an agent's reputation profile (cached for 5 min).

        *agent_id_or_address* can be an integer agentId or a hex wallet address.
        """
        cache_key = str(agent_id_or_address)
        now = time.monotonic()

        cached = self._cache.get(cache_key)
        if cached and (now - cached[0]) < _CACHE_TTL:
            return cached[1]

        try:
            profile = self._build_profile(agent_id_or_address)
        except Exception:
            logger.exception("Failed to build reputation profile for %s", cache_key)
            profile = AgentProfile()  # neutral defaults

        self._cache[cache_key] = (now, profile)
        return profile

    @staticmethod
    def map_reputation_to_strategy(reputation_score: float) -> dict[str, Any]:
        """Map a reputation score to negotiation strategy parameters.

        Accepts scores on **either** a 0-1 or 0-100 scale (values ≤ 1 are
        treated as 0-1 and scaled up).

        Returns a dict consumed by the negotiation engine:
        - concession_rate: how quickly the agent concedes (0-1)
        - initial_offer_aggressiveness: how far from fair the first offer is (0-1)
        - walk_away_threshold: minimum acceptable utility before walking away (0-1)
        """
        # Normalise to 0-100
        score = reputation_score * 100.0 if reputation_score <= 1.0 else reputation_score

        if score > 80:
            # Highly trusted — cooperate more, concede faster
            return {
                "concession_rate": 0.15,
                "initial_offer_aggressiveness": 0.2,
                "walk_away_threshold": 0.3,
                "label": "cooperative",
            }
        elif score > 40:
            # Moderate trust — balanced strategy
            return {
                "concession_rate": 0.10,
                "initial_offer_aggressiveness": 0.4,
                "walk_away_threshold": 0.5,
                "label": "balanced",
            }
        else:
            # Low trust — play it safe
            return {
                "concession_rate": 0.05,
                "initial_offer_aggressiveness": 0.7,
                "walk_away_threshold": 0.7,
                "label": "aggressive",
            }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_profile(self, agent_id_or_address: int | str) -> AgentProfile:
        """Assemble a profile from on-chain data.

        The returned :class:`AgentProfile` is the Pydantic model defined
        in ``core/types.py``.
        """
        # Determine agent_id vs address
        if isinstance(agent_id_or_address, int):
            agent_id_str = str(agent_id_or_address)
            agent_id = agent_id_or_address
            address = ""
        else:
            address = agent_id_or_address
            agent_id_str = address
            agent_id = 0  # unknown

        # Read reputation summary from ReputationRegistry
        pos, neg, neu = self._reputation.get_summary(
            agent_id, client_addresses=[], tag1="", tag2=""
        )
        total = pos + neg + neu
        score = (pos / total) if total > 0 else 0.5

        # Read deal statistics from DealRecord (only if we have an address)
        deal_count = 0
        if address:
            deal_count = self._deals.get_deal_count(address)

        return AgentProfile(
            agent_id=agent_id_str,
            wallet_address=address,
            reputation_score=score,
            deal_count=deal_count,
            strategy_params={
                "positive": pos,
                "negative": neg,
                "neutral": neu,
            },
        )
