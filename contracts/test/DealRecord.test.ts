import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("DealRecord", function () {
  async function deployFixture() {
    const [deployer, buyer, seller, outsider] = await ethers.getSigners();

    // Deploy IdentityRegistry
    const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
    const identityRegistry = await IdentityRegistry.deploy();

    // Deploy ReputationRegistry
    const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
    const reputationRegistry = await ReputationRegistry.deploy();

    // Initialize ReputationRegistry
    await reputationRegistry.initialize(await identityRegistry.getAddress());

    // Deploy DealRecord
    const DealRecord = await ethers.getContractFactory("DealRecord");
    const dealRecord = await DealRecord.deploy(
      await identityRegistry.getAddress(),
      await reputationRegistry.getAddress()
    );

    return { dealRecord, identityRegistry, reputationRegistry, deployer, buyer, seller, outsider };
  }

  function makeAttestation(buyer: string, seller: string, overrides?: Partial<any>) {
    return {
      dealHash: ethers.ZeroHash,
      buyer,
      seller,
      buyerAgentId: 1,
      sellerAgentId: 2,
      resourceUri: "https://api.example.com/llm/v1/chat",
      openingBuyerPrice: 30000,
      openingSellerPrice: 50000,
      finalPrice: 38000,
      negotiationRounds: 5,
      sla: {
        responseTimeMs: 500,
        availabilityBps: 9900,
        validityPeriodSecs: 86400,
      },
      x402TxHash: ethers.ZeroHash,
      timestamp: Math.floor(Date.now() / 1000),
      settled: false,
      ...overrides,
    };
  }

  describe("recordDeal", function () {
    it("should record a deal and emit DealRecorded event", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);

      const tx = await dealRecord.recordDeal(attestation);
      const receipt = await tx.wait();

      // Check event was emitted
      await expect(tx)
        .to.emit(dealRecord, "DealRecorded")
        .withArgs(
          // dealHash is computed on-chain, match any bytes32
          (hash: string) => ethers.isHexString(hash, 32),
          buyer.address,
          seller.address,
          38000,
          5
        );

      // Verify deal count incremented
      expect(await dealRecord.getDealCount(buyer.address)).to.equal(1);
      expect(await dealRecord.getDealCount(seller.address)).to.equal(1);
    });

    it("should reject a deal with zero price", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address, {
        finalPrice: 0,
      });

      await expect(dealRecord.recordDeal(attestation)).to.be.revertedWith(
        "DealRecord: zero price"
      );
    });

    it("should reject a deal with zero buyer address", async function () {
      const { dealRecord, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(ethers.ZeroAddress, seller.address);

      await expect(dealRecord.recordDeal(attestation)).to.be.revertedWith(
        "DealRecord: invalid buyer"
      );
    });
  });

  describe("settleDeal", function () {
    it("should settle a deal and emit DealSettled event", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);
      const tx = await dealRecord.recordDeal(attestation);
      const receipt = await tx.wait();

      // Extract dealHash from the event
      const event = receipt!.logs.find(
        (log: any) => log.fragment?.name === "DealRecorded"
      ) as any;
      const dealHash = event.args[0];

      const x402TxHash = ethers.keccak256(ethers.toUtf8Bytes("x402-settlement-tx"));

      // Buyer settles
      await expect(dealRecord.connect(buyer).settleDeal(dealHash, x402TxHash))
        .to.emit(dealRecord, "DealSettled")
        .withArgs(dealHash, x402TxHash);

      // Verify deal is settled
      const deal = await dealRecord.getDeal(dealHash);
      expect(deal.settled).to.be.true;
      expect(deal.x402TxHash).to.equal(x402TxHash);
    });

    it("should reject unauthorized settle attempts", async function () {
      const { dealRecord, buyer, seller, outsider } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);
      const tx = await dealRecord.recordDeal(attestation);
      const receipt = await tx.wait();

      const event = receipt!.logs.find(
        (log: any) => log.fragment?.name === "DealRecorded"
      ) as any;
      const dealHash = event.args[0];

      const x402TxHash = ethers.keccak256(ethers.toUtf8Bytes("x402-settlement-tx"));

      await expect(
        dealRecord.connect(outsider).settleDeal(dealHash, x402TxHash)
      ).to.be.revertedWith("DealRecord: unauthorized");
    });

    it("should reject double settlement", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);
      const tx = await dealRecord.recordDeal(attestation);
      const receipt = await tx.wait();

      const event = receipt!.logs.find(
        (log: any) => log.fragment?.name === "DealRecorded"
      ) as any;
      const dealHash = event.args[0];

      const x402TxHash = ethers.keccak256(ethers.toUtf8Bytes("x402-settlement-tx"));

      await dealRecord.connect(buyer).settleDeal(dealHash, x402TxHash);

      await expect(
        dealRecord.connect(seller).settleDeal(dealHash, x402TxHash)
      ).to.be.revertedWith("DealRecord: already settled");
    });
  });

  describe("tracking", function () {
    it("should track deal count and volume per agent", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      // Record first deal
      const att1 = makeAttestation(buyer.address, seller.address, {
        finalPrice: 38000,
        negotiationRounds: 5,
        timestamp: 1000,
      });
      await dealRecord.recordDeal(att1);

      // Record second deal with different parameters to avoid duplicate hash
      const att2 = makeAttestation(buyer.address, seller.address, {
        finalPrice: 45000,
        negotiationRounds: 3,
        timestamp: 2000,
      });
      await dealRecord.recordDeal(att2);

      // Verify counts
      expect(await dealRecord.getDealCount(buyer.address)).to.equal(2);
      expect(await dealRecord.getDealCount(seller.address)).to.equal(2);

      // Verify volume
      expect(await dealRecord.getTotalVolume(buyer.address)).to.equal(83000);
      expect(await dealRecord.getTotalVolume(seller.address)).to.equal(83000);

      // Verify average rounds: (5 + 3) / 2 = 4
      expect(await dealRecord.getAvgRounds(buyer.address)).to.equal(4);
    });

    it("should return deals by agent", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);
      await dealRecord.recordDeal(attestation);

      const buyerDeals = await dealRecord.getDealsByAgent(buyer.address);
      const sellerDeals = await dealRecord.getDealsByAgent(seller.address);

      expect(buyerDeals.length).to.equal(1);
      expect(sellerDeals.length).to.equal(1);
      expect(buyerDeals[0]).to.equal(sellerDeals[0]);
    });
  });

  describe("updateReputation", function () {
    it("should emit ReputationUpdated events for both agents", async function () {
      const { dealRecord, buyer, seller } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);
      const tx = await dealRecord.recordDeal(attestation);
      const receipt = await tx.wait();

      const event = receipt!.logs.find(
        (log: any) => log.fragment?.name === "DealRecorded"
      ) as any;
      const dealHash = event.args[0];

      await expect(
        dealRecord.connect(buyer).updateReputation(dealHash, 85, 90, "pricing_fairness")
      )
        .to.emit(dealRecord, "ReputationUpdated")
        .withArgs(dealHash, buyer.address, 85, "pricing_fairness")
        .and.to.emit(dealRecord, "ReputationUpdated")
        .withArgs(dealHash, seller.address, 90, "pricing_fairness");
    });

    it("should reject unauthorized reputation updates", async function () {
      const { dealRecord, buyer, seller, outsider } = await loadFixture(deployFixture);

      const attestation = makeAttestation(buyer.address, seller.address);
      const tx = await dealRecord.recordDeal(attestation);
      const receipt = await tx.wait();

      const event = receipt!.logs.find(
        (log: any) => log.fragment?.name === "DealRecorded"
      ) as any;
      const dealHash = event.args[0];

      await expect(
        dealRecord.connect(outsider).updateReputation(dealHash, 85, 90, "pricing_fairness")
      ).to.be.revertedWith("DealRecord: unauthorized");
    });
  });
});

describe("IdentityRegistry", function () {
  async function deployFixture() {
    const [deployer, agent1, agent2] = await ethers.getSigners();
    const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
    const registry = await IdentityRegistry.deploy();
    return { registry, deployer, agent1, agent2 };
  }

  it("should register an agent with URI", async function () {
    const { registry, agent1 } = await loadFixture(deployFixture);

    const agentURI = "https://buyer.negotiatorgrid.dev/.well-known/agent-card.json";

    await expect(registry.connect(agent1)["register(string)"](agentURI))
      .to.emit(registry, "Registered")
      .withArgs(1, agentURI, agent1.address);

    expect(await registry.tokenURI(1)).to.equal(agentURI);
    expect(await registry.ownerOf(1)).to.equal(agent1.address);
    expect(await registry.totalAgents()).to.equal(1);
  });

  it("should register with URI and metadata", async function () {
    const { registry, agent1 } = await loadFixture(deployFixture);

    const metadata = [
      {
        metadataKey: "service",
        metadataValue: ethers.toUtf8Bytes("A2A"),
      },
    ];

    await registry
      .connect(agent1)
      ["register(string,(string,bytes)[])"](
        "https://agent.example.com",
        metadata
      );

    const value = await registry.getMetadata(1, "service");
    expect(ethers.toUtf8String(value)).to.equal("A2A");
  });

  it("should update agent URI", async function () {
    const { registry, agent1 } = await loadFixture(deployFixture);

    await registry.connect(agent1)["register(string)"]("https://old-uri.com");

    await expect(registry.connect(agent1).setAgentURI(1, "https://new-uri.com"))
      .to.emit(registry, "URIUpdated")
      .withArgs(1, "https://new-uri.com", agent1.address);

    expect(await registry.tokenURI(1)).to.equal("https://new-uri.com");
  });

  it("should reject URI update from non-owner", async function () {
    const { registry, agent1, agent2 } = await loadFixture(deployFixture);

    await registry.connect(agent1)["register(string)"]("https://old-uri.com");

    await expect(
      registry.connect(agent2).setAgentURI(1, "https://hacked.com")
    ).to.be.revertedWith("IdentityRegistry: not agent owner");
  });
});

describe("ReputationRegistry", function () {
  async function deployFixture() {
    const [deployer, client1, client2] = await ethers.getSigners();

    const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
    const identityRegistry = await IdentityRegistry.deploy();

    const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
    const reputationRegistry = await ReputationRegistry.deploy();
    await reputationRegistry.initialize(await identityRegistry.getAddress());

    // Register an agent
    await identityRegistry.connect(client1)["register(string)"]("https://agent.example.com");

    return { reputationRegistry, identityRegistry, deployer, client1, client2 };
  }

  it("should give feedback and emit NewFeedback event", async function () {
    const { reputationRegistry, client2 } = await loadFixture(deployFixture);

    await expect(
      reputationRegistry
        .connect(client2)
        .giveFeedback(
          1,
          85,
          2,
          "pricing_fairness",
          "buyer",
          "https://api.example.com/v1",
          "ipfs://feedback-hash",
          ethers.keccak256(ethers.toUtf8Bytes("feedback-content"))
        )
    ).to.emit(reputationRegistry, "NewFeedback");
  });

  it("should revoke feedback", async function () {
    const { reputationRegistry, client2 } = await loadFixture(deployFixture);

    await reputationRegistry
      .connect(client2)
      .giveFeedback(1, 85, 2, "pricing_fairness", "buyer", "", "", ethers.ZeroHash);

    await expect(reputationRegistry.connect(client2).revokeFeedback(1, 1))
      .to.emit(reputationRegistry, "FeedbackRevoked")
      .withArgs(1, client2.address, 1);
  });

  it("should compute summary correctly", async function () {
    const { reputationRegistry, client1, client2 } = await loadFixture(deployFixture);

    // Two feedbacks from different clients
    await reputationRegistry
      .connect(client1)
      .giveFeedback(1, 80, 0, "pricing_fairness", "buyer", "", "", ethers.ZeroHash);
    await reputationRegistry
      .connect(client2)
      .giveFeedback(1, 90, 0, "pricing_fairness", "buyer", "", "", ethers.ZeroHash);

    const [count, summaryValue] = await reputationRegistry.getSummary(
      1,
      [],
      "pricing_fairness",
      "buyer"
    );

    expect(count).to.equal(2);
    expect(summaryValue).to.equal(170); // 80 + 90
  });
});
