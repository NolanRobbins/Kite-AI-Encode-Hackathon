// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/// @title IdentityRegistry (ERC-8004)
/// @notice Agent registration as ERC-721 NFTs with URI-based metadata
/// @dev Simplified implementation of ERC-8004 Identity Registry for Kite Testnet
contract IdentityRegistry is ERC721URIStorage {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // ========================================================================
    // TYPES
    // ========================================================================

    struct MetadataEntry {
        string metadataKey;
        bytes metadataValue;
    }

    // ========================================================================
    // STATE
    // ========================================================================

    /// @notice Auto-incrementing agent ID counter
    uint256 private _nextAgentId;

    /// @notice agentId => metadataKey => metadataValue
    mapping(uint256 => mapping(string => bytes)) private _metadata;

    /// @notice agentId => wallet address designated for payments
    mapping(uint256 => address) private _agentWallets;

    // ========================================================================
    // EVENTS
    // ========================================================================

    event Registered(uint256 indexed agentId, string agentURI, address indexed owner);
    event URIUpdated(uint256 indexed agentId, string newURI, address indexed updatedBy);
    event MetadataSet(
        uint256 indexed agentId,
        string indexed indexedMetadataKey,
        string metadataKey,
        bytes metadataValue
    );

    // ========================================================================
    // CONSTRUCTOR
    // ========================================================================

    constructor() ERC721("NegotiatorGrid Agent", "NGAGENT") {
        _nextAgentId = 1;
    }

    // ========================================================================
    // REGISTRATION
    // ========================================================================

    /// @notice Register a new agent with URI and metadata entries
    /// @param agentURI The URI pointing to the agent's registration file
    /// @param metadata Array of key-value metadata entries to set on registration
    /// @return agentId The newly minted agent NFT token ID
    function register(string calldata agentURI, MetadataEntry[] calldata metadata)
        external
        returns (uint256 agentId)
    {
        agentId = _nextAgentId++;
        _safeMint(msg.sender, agentId);
        _setTokenURI(agentId, agentURI);

        for (uint256 i = 0; i < metadata.length; i++) {
            _metadata[agentId][metadata[i].metadataKey] = metadata[i].metadataValue;
            emit MetadataSet(
                agentId,
                metadata[i].metadataKey,
                metadata[i].metadataKey,
                metadata[i].metadataValue
            );
        }

        emit Registered(agentId, agentURI, msg.sender);
    }

    /// @notice Register a new agent with just a URI
    /// @param agentURI The URI pointing to the agent's registration file
    /// @return agentId The newly minted agent NFT token ID
    function register(string calldata agentURI) external returns (uint256 agentId) {
        agentId = _nextAgentId++;
        _safeMint(msg.sender, agentId);
        _setTokenURI(agentId, agentURI);
        emit Registered(agentId, agentURI, msg.sender);
    }

    /// @notice Register a new agent with no URI (can be set later)
    /// @return agentId The newly minted agent NFT token ID
    function register() external returns (uint256 agentId) {
        agentId = _nextAgentId++;
        _safeMint(msg.sender, agentId);
        emit Registered(agentId, "", msg.sender);
    }

    // ========================================================================
    // URI MANAGEMENT
    // ========================================================================

    /// @notice Update the URI for an agent
    /// @param agentId The agent NFT token ID
    /// @param newURI The new URI to set
    function setAgentURI(uint256 agentId, string calldata newURI) external {
        require(ownerOf(agentId) == msg.sender, "IdentityRegistry: not agent owner");
        _setTokenURI(agentId, newURI);
        emit URIUpdated(agentId, newURI, msg.sender);
    }

    // ========================================================================
    // ON-CHAIN METADATA
    // ========================================================================

    /// @notice Get a metadata value for an agent
    /// @param agentId The agent NFT token ID
    /// @param metadataKey The metadata key to look up
    /// @return The metadata value as bytes
    function getMetadata(uint256 agentId, string memory metadataKey)
        external
        view
        returns (bytes memory)
    {
        require(_ownerOf(agentId) != address(0), "IdentityRegistry: agent does not exist");
        return _metadata[agentId][metadataKey];
    }

    /// @notice Set a metadata value for an agent
    /// @param agentId The agent NFT token ID
    /// @param metadataKey The metadata key
    /// @param metadataValue The metadata value as bytes
    function setMetadata(uint256 agentId, string memory metadataKey, bytes memory metadataValue)
        external
    {
        require(ownerOf(agentId) == msg.sender, "IdentityRegistry: not agent owner");
        _metadata[agentId][metadataKey] = metadataValue;
        emit MetadataSet(agentId, metadataKey, metadataKey, metadataValue);
    }

    // ========================================================================
    // AGENT WALLET
    // ========================================================================

    /// @notice Set a designated payment wallet for an agent
    /// @dev Requires a signed message from the new wallet proving ownership
    /// @param agentId The agent NFT token ID
    /// @param newWallet The wallet address to designate for payments
    /// @param deadline Timestamp after which the signature is no longer valid
    /// @param signature EIP-191 signature from newWallet over (agentId, owner, deadline)
    function setAgentWallet(
        uint256 agentId,
        address newWallet,
        uint256 deadline,
        bytes calldata signature
    ) external {
        require(ownerOf(agentId) == msg.sender, "IdentityRegistry: not agent owner");
        require(block.timestamp <= deadline, "IdentityRegistry: signature expired");

        bytes32 messageHash = keccak256(
            abi.encodePacked(agentId, msg.sender, newWallet, deadline)
        );
        bytes32 ethSignedHash = messageHash.toEthSignedMessageHash();
        address recovered = ethSignedHash.recover(signature);
        require(recovered == newWallet, "IdentityRegistry: invalid wallet signature");

        _agentWallets[agentId] = newWallet;
    }

    /// @notice Get the designated payment wallet for an agent
    /// @param agentId The agent NFT token ID
    /// @return The designated wallet address (address(0) if not set)
    function getAgentWallet(uint256 agentId) external view returns (address) {
        require(_ownerOf(agentId) != address(0), "IdentityRegistry: agent does not exist");
        return _agentWallets[agentId];
    }

    /// @notice Remove the designated payment wallet for an agent
    /// @param agentId The agent NFT token ID
    function unsetAgentWallet(uint256 agentId) external {
        require(ownerOf(agentId) == msg.sender, "IdentityRegistry: not agent owner");
        delete _agentWallets[agentId];
    }

    // ========================================================================
    // VIEW HELPERS
    // ========================================================================

    /// @notice Get the total number of registered agents
    /// @return The next agent ID minus 1 (total minted)
    function totalAgents() external view returns (uint256) {
        return _nextAgentId - 1;
    }
}
