import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const NegotiatorGridModule = buildModule("NegotiatorGrid", (m) => {
  // 1. Deploy Identity Registry (ERC-721 agent NFTs)
  const identityRegistry = m.contract("IdentityRegistry", []);

  // 2. Deploy Reputation Registry
  const reputationRegistry = m.contract("ReputationRegistry", []);

  // 3. Initialize Reputation Registry with Identity Registry address
  m.call(reputationRegistry, "initialize", [identityRegistry]);

  // 4. Deploy DealRecord with both registry addresses
  const dealRecord = m.contract("DealRecord", [identityRegistry, reputationRegistry]);

  return { identityRegistry, reputationRegistry, dealRecord };
});

export default NegotiatorGridModule;
