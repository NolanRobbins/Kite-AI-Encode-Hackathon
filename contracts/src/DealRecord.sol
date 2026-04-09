// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// @title DealRecord
/// @notice On-chain attestation of NegotiatorGrid negotiation outcomes
/// @dev Stores deal terms and links to x402 settlement transactions
contract DealRecord {

    // ========================================================================
    // TYPES
    // ========================================================================

    struct SLATerms {
        uint64 responseTimeMs;      // Max response time promised (ms)
        uint64 availabilityBps;     // Uptime guarantee in basis points (9900 = 99%)
        uint64 validityPeriodSecs;  // How long the deal terms are valid
    }

    struct DealAttestation {
        bytes32 dealHash;           // keccak256(buyer, seller, price, resource, ts, nonce)
        address buyer;              // Buyer agent wallet address
        address seller;             // Seller agent wallet address
        uint256 buyerAgentId;       // ERC-8004 agentId of buyer (0 if not registered)
        uint256 sellerAgentId;      // ERC-8004 agentId of seller (0 if not registered)
        string resourceUri;         // Resource being purchased
        uint256 openingBuyerPrice;  // Buyer's opening offer (atomic units)
        uint256 openingSellerPrice; // Seller's opening ask (atomic units)
        uint256 finalPrice;         // Agreed price (atomic units)
        uint8 negotiationRounds;    // Number of rounds to agreement
        SLATerms sla;              // Service-level agreement terms
        bytes32 x402TxHash;         // x402 settlement transaction hash (0x0 if pending)
        uint64 timestamp;           // Block timestamp of attestation
        bool settled;               // Whether x402 payment has settled
    }

    // ========================================================================
    // STATE
    // ========================================================================

    /// @notice Address of the IdentityRegistry contract
    address public identityRegistry;

    /// @notice Address of the ReputationRegistry contract
    address public reputationRegistry;

    /// @notice dealHash => DealAttestation
    mapping(bytes32 => DealAttestation) private _deals;

    /// @notice agent address => list of deal hashes
    mapping(address => bytes32[]) private _agentDeals;

    /// @notice agent address => total negotiation rounds across all deals
    mapping(address => uint256) private _totalRounds;

    /// @notice agent address => total trade volume
    mapping(address => uint256) private _totalVolume;

    // ========================================================================
    // EVENTS
    // ========================================================================

    event DealRecorded(
        bytes32 indexed dealHash,
        address indexed buyer,
        address indexed seller,
        uint256 finalPrice,
        uint8 negotiationRounds
    );

    event DealSettled(
        bytes32 indexed dealHash,
        bytes32 x402TxHash
    );

    event ReputationUpdated(
        bytes32 indexed dealHash,
        address indexed agent,
        int128 score,
        string tag
    );

    // ========================================================================
    // CONSTRUCTOR
    // ========================================================================

    /// @param identityRegistry_ Address of the IdentityRegistry contract
    /// @param reputationRegistry_ Address of the ReputationRegistry contract
    constructor(address identityRegistry_, address reputationRegistry_) {
        identityRegistry = identityRegistry_;
        reputationRegistry = reputationRegistry_;
    }

    // ========================================================================
    // WRITE FUNCTIONS
    // ========================================================================

    /// @notice Record a completed negotiation deal
    /// @param attestation The deal attestation data
    /// @return dealHash The unique identifier for this deal
    function recordDeal(DealAttestation calldata attestation) external returns (bytes32 dealHash) {
        dealHash = keccak256(
            abi.encodePacked(
                attestation.buyer,
                attestation.seller,
                attestation.finalPrice,
                attestation.resourceUri,
                attestation.timestamp,
                attestation.negotiationRounds
            )
        );

        require(_deals[dealHash].buyer == address(0), "DealRecord: deal already exists");
        require(attestation.buyer != address(0), "DealRecord: invalid buyer");
        require(attestation.seller != address(0), "DealRecord: invalid seller");
        require(attestation.finalPrice > 0, "DealRecord: zero price");

        DealAttestation storage deal = _deals[dealHash];
        deal.dealHash = dealHash;
        deal.buyer = attestation.buyer;
        deal.seller = attestation.seller;
        deal.buyerAgentId = attestation.buyerAgentId;
        deal.sellerAgentId = attestation.sellerAgentId;
        deal.resourceUri = attestation.resourceUri;
        deal.openingBuyerPrice = attestation.openingBuyerPrice;
        deal.openingSellerPrice = attestation.openingSellerPrice;
        deal.finalPrice = attestation.finalPrice;
        deal.negotiationRounds = attestation.negotiationRounds;
        deal.sla = attestation.sla;
        deal.x402TxHash = bytes32(0);
        deal.timestamp = uint64(block.timestamp);
        deal.settled = false;

        _agentDeals[attestation.buyer].push(dealHash);
        _agentDeals[attestation.seller].push(dealHash);

        _totalRounds[attestation.buyer] += attestation.negotiationRounds;
        _totalRounds[attestation.seller] += attestation.negotiationRounds;

        _totalVolume[attestation.buyer] += attestation.finalPrice;
        _totalVolume[attestation.seller] += attestation.finalPrice;

        emit DealRecorded(
            dealHash,
            attestation.buyer,
            attestation.seller,
            attestation.finalPrice,
            attestation.negotiationRounds
        );
    }

    /// @notice Mark a deal as settled with the x402 transaction hash
    /// @param dealHash The deal to update
    /// @param x402TxHash The on-chain settlement transaction hash
    function settleDeal(bytes32 dealHash, bytes32 x402TxHash) external {
        DealAttestation storage deal = _deals[dealHash];
        require(deal.buyer != address(0), "DealRecord: deal does not exist");
        require(!deal.settled, "DealRecord: already settled");
        require(
            msg.sender == deal.buyer || msg.sender == deal.seller,
            "DealRecord: unauthorized"
        );

        deal.x402TxHash = x402TxHash;
        deal.settled = true;

        emit DealSettled(dealHash, x402TxHash);
    }

    /// @notice Update reputation scores for both agents after deal completion
    /// @param dealHash The deal to update reputation for
    /// @param buyerScore Buyer's performance score
    /// @param sellerScore Seller's performance score
    /// @param tag Reputation category (e.g., "pricing_fairness", "delivery_speed")
    function updateReputation(
        bytes32 dealHash,
        int128 buyerScore,
        int128 sellerScore,
        string calldata tag
    ) external {
        DealAttestation storage deal = _deals[dealHash];
        require(deal.buyer != address(0), "DealRecord: deal does not exist");
        require(
            msg.sender == deal.buyer || msg.sender == deal.seller,
            "DealRecord: unauthorized"
        );

        emit ReputationUpdated(dealHash, deal.buyer, buyerScore, tag);
        emit ReputationUpdated(dealHash, deal.seller, sellerScore, tag);
    }

    // ========================================================================
    // READ FUNCTIONS
    // ========================================================================

    /// @notice Get a deal attestation by hash
    /// @param dealHash The unique deal identifier
    /// @return The full DealAttestation struct
    function getDeal(bytes32 dealHash) external view returns (DealAttestation memory) {
        require(_deals[dealHash].buyer != address(0), "DealRecord: deal does not exist");
        return _deals[dealHash];
    }

    /// @notice Get all deals for an agent address
    /// @param agent The agent's wallet address
    /// @return dealHashes Array of deal hashes involving this agent
    function getDealsByAgent(address agent) external view returns (bytes32[] memory dealHashes) {
        return _agentDeals[agent];
    }

    /// @notice Get deal count for an agent
    /// @param agent The agent's wallet address
    /// @return Number of deals involving this agent
    function getDealCount(address agent) external view returns (uint256) {
        return _agentDeals[agent].length;
    }

    /// @notice Get average negotiation rounds for an agent
    /// @param agent The agent's wallet address
    /// @return Average rounds (0 if no deals)
    function getAvgRounds(address agent) external view returns (uint256) {
        uint256 count = _agentDeals[agent].length;
        if (count == 0) return 0;
        return _totalRounds[agent] / count;
    }

    /// @notice Get total volume traded by an agent
    /// @param agent The agent's wallet address
    /// @return Total volume in atomic units
    function getTotalVolume(address agent) external view returns (uint256) {
        return _totalVolume[agent];
    }

    /// @notice Verify a deal hash matches the expected computation
    /// @param dealHash The deal hash to verify
    /// @param attestation The attestation data to verify against
    /// @return True if the hash matches
    function verifyDealHash(bytes32 dealHash, DealAttestation calldata attestation)
        external
        pure
        returns (bool)
    {
        bytes32 computed = keccak256(
            abi.encodePacked(
                attestation.buyer,
                attestation.seller,
                attestation.finalPrice,
                attestation.resourceUri,
                attestation.timestamp,
                attestation.negotiationRounds
            )
        );
        return dealHash == computed;
    }
}
