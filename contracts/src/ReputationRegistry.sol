// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// @title ReputationRegistry (ERC-8004)
/// @notice Structured feedback system for agent reputation on NegotiatorGrid
/// @dev Implements the ERC-8004 Reputation Registry interface
contract ReputationRegistry {

    // ========================================================================
    // TYPES
    // ========================================================================

    struct Feedback {
        int128 value;
        uint8 valueDecimals;
        string tag1;
        string tag2;
        string endpoint;
        string feedbackURI;
        bytes32 feedbackHash;
        bool isRevoked;
        address client;
    }

    // ========================================================================
    // STATE
    // ========================================================================

    /// @notice Address of the linked IdentityRegistry
    address public identityRegistry;

    /// @notice Whether the contract has been initialized
    bool private _initialized;

    /// @notice agentId => client => feedbackIndex => Feedback
    mapping(uint256 => mapping(address => mapping(uint64 => Feedback))) private _feedbacks;

    /// @notice agentId => client => last feedback index
    mapping(uint256 => mapping(address => uint64)) private _lastIndex;

    /// @notice agentId => list of unique client addresses
    mapping(uint256 => address[]) private _clients;

    /// @notice agentId => client => whether client has previously given feedback
    mapping(uint256 => mapping(address => bool)) private _isClient;

    // ========================================================================
    // EVENTS
    // ========================================================================

    event NewFeedback(
        uint256 indexed agentId,
        address indexed clientAddress,
        uint64 feedbackIndex,
        int128 value,
        uint8 valueDecimals,
        string indexed indexedTag1,
        string tag1,
        string tag2,
        string endpoint,
        string feedbackURI,
        bytes32 feedbackHash
    );

    event FeedbackRevoked(
        uint256 indexed agentId,
        address indexed clientAddress,
        uint64 indexed feedbackIndex
    );

    event ResponseAppended(
        uint256 indexed agentId,
        address indexed clientAddress,
        uint64 feedbackIndex,
        address indexed responder,
        string responseURI,
        bytes32 responseHash
    );

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    /// @notice Initialize the registry with the IdentityRegistry address
    /// @param identityRegistry_ The address of the IdentityRegistry contract
    function initialize(address identityRegistry_) external {
        require(!_initialized, "ReputationRegistry: already initialized");
        require(identityRegistry_ != address(0), "ReputationRegistry: zero address");
        identityRegistry = identityRegistry_;
        _initialized = true;
    }

    /// @notice Get the linked IdentityRegistry address
    /// @return The IdentityRegistry contract address
    function getIdentityRegistry() external view returns (address) {
        return identityRegistry;
    }

    // ========================================================================
    // FEEDBACK
    // ========================================================================

    /// @notice Give feedback for an agent
    /// @param agentId The ERC-8004 agent ID
    /// @param value The feedback score
    /// @param valueDecimals Decimal precision of the value
    /// @param tag1 Primary feedback category (e.g., "pricing_fairness")
    /// @param tag2 Secondary feedback category (e.g., "buyer")
    /// @param endpoint The service endpoint being rated
    /// @param feedbackURI URI to detailed feedback (e.g., IPFS hash)
    /// @param feedbackHash Hash of the feedback content for integrity
    function giveFeedback(
        uint256 agentId,
        int128 value,
        uint8 valueDecimals,
        string calldata tag1,
        string calldata tag2,
        string calldata endpoint,
        string calldata feedbackURI,
        bytes32 feedbackHash
    ) external {
        require(_initialized, "ReputationRegistry: not initialized");

        uint64 feedbackIndex = _lastIndex[agentId][msg.sender] + 1;
        _lastIndex[agentId][msg.sender] = feedbackIndex;

        _feedbacks[agentId][msg.sender][feedbackIndex] = Feedback({
            value: value,
            valueDecimals: valueDecimals,
            tag1: tag1,
            tag2: tag2,
            endpoint: endpoint,
            feedbackURI: feedbackURI,
            feedbackHash: feedbackHash,
            isRevoked: false,
            client: msg.sender
        });

        if (!_isClient[agentId][msg.sender]) {
            _isClient[agentId][msg.sender] = true;
            _clients[agentId].push(msg.sender);
        }

        emit NewFeedback(
            agentId,
            msg.sender,
            feedbackIndex,
            value,
            valueDecimals,
            tag1,
            tag1,
            tag2,
            endpoint,
            feedbackURI,
            feedbackHash
        );
    }

    /// @notice Revoke previously given feedback
    /// @param agentId The ERC-8004 agent ID
    /// @param feedbackIndex The index of the feedback to revoke
    function revokeFeedback(uint256 agentId, uint64 feedbackIndex) external {
        Feedback storage fb = _feedbacks[agentId][msg.sender][feedbackIndex];
        require(fb.client == msg.sender, "ReputationRegistry: not feedback author");
        require(!fb.isRevoked, "ReputationRegistry: already revoked");

        fb.isRevoked = true;

        emit FeedbackRevoked(agentId, msg.sender, feedbackIndex);
    }

    /// @notice Append a response to existing feedback
    /// @param agentId The ERC-8004 agent ID
    /// @param clientAddress The address of the original feedback author
    /// @param feedbackIndex The index of the feedback to respond to
    /// @param responseURI URI to the response content
    /// @param responseHash Hash of the response content for integrity
    function appendResponse(
        uint256 agentId,
        address clientAddress,
        uint64 feedbackIndex,
        string calldata responseURI,
        bytes32 responseHash
    ) external {
        Feedback storage fb = _feedbacks[agentId][clientAddress][feedbackIndex];
        require(fb.client != address(0), "ReputationRegistry: feedback does not exist");

        emit ResponseAppended(
            agentId,
            clientAddress,
            feedbackIndex,
            msg.sender,
            responseURI,
            responseHash
        );
    }

    // ========================================================================
    // READ FUNCTIONS
    // ========================================================================

    /// @notice Get aggregated feedback summary for an agent
    /// @param agentId The ERC-8004 agent ID
    /// @param clientAddresses Filter by specific client addresses (empty = all)
    /// @param tag1 Filter by primary tag (empty = all)
    /// @param tag2 Filter by secondary tag (empty = all)
    /// @return count Number of matching feedbacks
    /// @return summaryValue Aggregated feedback value
    /// @return summaryValueDecimals Decimal precision of the summary value
    function getSummary(
        uint256 agentId,
        address[] calldata clientAddresses,
        string calldata tag1,
        string calldata tag2
    ) external view returns (uint64 count, int128 summaryValue, uint8 summaryValueDecimals) {
        address[] memory clients;
        if (clientAddresses.length > 0) {
            clients = new address[](clientAddresses.length);
            for (uint256 i = 0; i < clientAddresses.length; i++) {
                clients[i] = clientAddresses[i];
            }
        } else {
            clients = _clients[agentId];
        }

        int256 total = 0;
        uint8 maxDecimals = 0;

        for (uint256 c = 0; c < clients.length; c++) {
            uint64 lastIdx = _lastIndex[agentId][clients[c]];
            for (uint64 i = 1; i <= lastIdx; i++) {
                Feedback storage fb = _feedbacks[agentId][clients[c]][i];
                if (fb.isRevoked) continue;

                bool matchTag1 = bytes(tag1).length == 0 ||
                    keccak256(bytes(fb.tag1)) == keccak256(bytes(tag1));
                bool matchTag2 = bytes(tag2).length == 0 ||
                    keccak256(bytes(fb.tag2)) == keccak256(bytes(tag2));

                if (matchTag1 && matchTag2) {
                    total += int256(fb.value);
                    count++;
                    if (fb.valueDecimals > maxDecimals) {
                        maxDecimals = fb.valueDecimals;
                    }
                }
            }
        }

        summaryValue = int128(total);
        summaryValueDecimals = maxDecimals;
    }

    /// @notice Read a specific feedback entry
    /// @param agentId The ERC-8004 agent ID
    /// @param clientAddress The feedback author's address
    /// @param feedbackIndex The feedback index
    /// @return value The feedback score
    /// @return valueDecimals Decimal precision
    /// @return tag1 Primary feedback category
    /// @return tag2 Secondary feedback category
    /// @return isRevoked Whether the feedback has been revoked
    function readFeedback(
        uint256 agentId,
        address clientAddress,
        uint64 feedbackIndex
    )
        external
        view
        returns (
            int128 value,
            uint8 valueDecimals,
            string memory tag1,
            string memory tag2,
            bool isRevoked
        )
    {
        Feedback storage fb = _feedbacks[agentId][clientAddress][feedbackIndex];
        return (fb.value, fb.valueDecimals, fb.tag1, fb.tag2, fb.isRevoked);
    }

    /// @notice Get all client addresses that have given feedback to an agent
    /// @param agentId The ERC-8004 agent ID
    /// @return Array of client addresses
    function getClients(uint256 agentId) external view returns (address[] memory) {
        return _clients[agentId];
    }

    /// @notice Get the last feedback index for a client-agent pair
    /// @param agentId The ERC-8004 agent ID
    /// @param clientAddress The client's address
    /// @return The last feedback index (0 if no feedback given)
    function getLastIndex(uint256 agentId, address clientAddress) external view returns (uint64) {
        return _lastIndex[agentId][clientAddress];
    }
}
