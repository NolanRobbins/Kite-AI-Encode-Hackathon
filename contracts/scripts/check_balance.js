// Verify the throwaway wallet has KITE balance before attempting deploy.
//
// Usage:  node scripts/check_balance.js
//
// Reads PRIVATE_KEY from ./.env, derives the address, queries Kite testnet
// RPC for the balance, and prints a human-readable result. Exits non-zero
// if the balance is below the minimum needed for the 3-contract deploy.

const fs = require("fs");
const path = require("path");
require("dotenv").config({ path: path.resolve(__dirname, "..", ".env") });

const { JsonRpcProvider, Wallet, formatEther } = require("ethers");

const RPC_URL = "https://rpc-testnet.gokite.ai/";
const MIN_BALANCE_WEI = 10n ** 15n; // 0.001 KITE — generous; deploys cost much less

async function main() {
  const pk = process.env.PRIVATE_KEY;
  if (!pk || pk.startsWith("0x...")) {
    console.error("contracts/.env has no real PRIVATE_KEY. Run scripts/generate_wallet.js first.");
    process.exit(2);
  }
  const wallet = new Wallet(pk);
  const provider = new JsonRpcProvider(RPC_URL);
  const balance = await provider.getBalance(wallet.address);

  console.log("");
  console.log("================================================================");
  console.log(" Kite testnet balance check");
  console.log("================================================================");
  console.log("");
  console.log(" Address:  " + wallet.address);
  console.log(" RPC:      " + RPC_URL);
  console.log(" Balance:  " + formatEther(balance) + " KITE");
  console.log("");

  if (balance < MIN_BALANCE_WEI) {
    console.error(
      " Below minimum (0.001 KITE). Faucet at https://faucet.gokite.ai and retry."
    );
    process.exit(1);
  }
  console.log(" Sufficient balance. Ready to deploy.");
  console.log("");
}

main().catch((err) => {
  console.error("Balance check failed:", err.message || err);
  process.exit(3);
});
