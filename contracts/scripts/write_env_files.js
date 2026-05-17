// Propagate deployed contract addresses + the throwaway private key into
// the .env files the Python backend and Next.js dashboard expect.
//
// Reads:
//   contracts/.env                                          (PRIVATE_KEY)
//   contracts/ignition/deployments/chain-2368/deployed_addresses.json
//
// Writes:
//   <repo_root>/.env                                        (backend)
//   <repo_root>/dashboard/.env.local                         (dashboard)
//
// Never prints the private key. Only prints addresses + filepaths.

const fs = require("fs");
const path = require("path");
require("dotenv").config({ path: path.resolve(__dirname, "..", ".env") });

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const BACKEND_ENV = path.resolve(REPO_ROOT, ".env");
const DASHBOARD_ENV = path.resolve(REPO_ROOT, "dashboard", ".env.local");

const ADDR_FILE = path.resolve(
  __dirname,
  "..",
  "ignition",
  "deployments",
  "chain-2368",
  "deployed_addresses.json"
);

const FORCE = process.argv.includes("--force");

function refuseOverwrite(filepath) {
  if (!fs.existsSync(filepath) || FORCE) return;
  console.error(
    "Refusing to overwrite existing " +
      filepath +
      ". Pass --force to override (your old env will be replaced)."
  );
  process.exit(1);
}

function privateKeyOrDie() {
  const pk = process.env.PRIVATE_KEY;
  if (!pk || pk.startsWith("0x...")) {
    console.error("contracts/.env has no real PRIVATE_KEY. Run generate_wallet.js first.");
    process.exit(2);
  }
  return pk;
}

function loadAddresses() {
  if (!fs.existsSync(ADDR_FILE)) {
    console.error("Deployed addresses file not found: " + ADDR_FILE);
    console.error("Run `npm run deploy:kite` first.");
    process.exit(3);
  }
  const raw = JSON.parse(fs.readFileSync(ADDR_FILE, "utf8"));
  return {
    identity: raw["NegotiatorGrid#IdentityRegistry"],
    reputation: raw["NegotiatorGrid#ReputationRegistry"],
    dealRecord: raw["NegotiatorGrid#DealRecord"],
  };
}

function buildBackendEnv(pk, addrs) {
  return [
    "# === NegotiatorGrid backend env ===",
    "# Generated " + new Date().toISOString() + " by contracts/scripts/write_env_files.js",
    "# Do NOT commit. Disposable throwaway key, testnet-only.",
    "",
    "# Kite Testnet",
    "KITE_RPC_URL=https://rpc-testnet.gokite.ai/",
    "KITE_CHAIN_ID=2368",
    "KITE_EXPLORER_URL=https://testnet.kitescan.ai/",
    "",
    "# Wallet (buyer signer; same key as contract deployer for hackathon simplicity)",
    "PRIVATE_KEY=" + pk,
    "",
    "# Deployed contracts (Kite Testnet 2368)",
    "IDENTITY_REGISTRY_ADDR=" + addrs.identity,
    "REPUTATION_REGISTRY_ADDR=" + addrs.reputation,
    "DEALRECORD_CONTRACT_ADDR=" + addrs.dealRecord,
    "",
    "# x402 / facilitator",
    "KITE_FACILITATOR_URL=https://facilitator.pieverse.io",
    "KITE_FACILITATOR_ADDR=0x12343e649e6b2b2b77649DFAb88f103c02F3C78b",
    "KITE_TEST_USDT_ADDR=0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63",
    "",
    "# Surprise API (local dev URL; replaced after Railway deploy)",
    "SURPRISE_API_URL=http://localhost:8001",
    "",
    "# LLM (optional; template fallback exists)",
    "OPENAI_API_KEY=",
    "OPENAI_MODEL=gpt-4o-mini",
    "",
    "# MCP",
    "KITE_MCP_ENDPOINT=https://neo.dev.gokite.ai/v1/mcp",
    "KITE_MCP_AUTH_TOKEN=",
    "",
    "# Kite Agent Passport (mock until live credentials available)",
    "KITE_PASSPORT_MODE=mock",
    "KITE_PASSPORT_AGENT_ID=",
    "KITE_PASSPORT_SESSION_ID=",
    "",
    "# Server",
    "API_HOST=0.0.0.0",
    "API_PORT=8000",
    "ALLOWED_ORIGINS=http://localhost:3000",
    "",
  ].join("\n");
}

function buildDashboardEnv() {
  return [
    "# === Dashboard env (local dev) ===",
    "# Generated " + new Date().toISOString() + " by contracts/scripts/write_env_files.js",
    "# Replace localhost URLs with Railway-deployed URLs before `npm run build` for Vercel.",
    "",
    "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000",
    "NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/negotiate",
    "NEXT_PUBLIC_KITE_TESTNET_EXPLORER=https://testnet.kitescan.ai",
    "",
  ].join("\n");
}

refuseOverwrite(BACKEND_ENV);
refuseOverwrite(DASHBOARD_ENV);

const pk = privateKeyOrDie();
const addrs = loadAddresses();

fs.mkdirSync(path.dirname(DASHBOARD_ENV), { recursive: true });

fs.writeFileSync(BACKEND_ENV, buildBackendEnv(pk, addrs), { mode: 0o600 });
fs.writeFileSync(DASHBOARD_ENV, buildDashboardEnv(), { mode: 0o600 });

console.log("");
console.log("================================================================");
console.log(" Wrote env files");
console.log("================================================================");
console.log("");
console.log(" Backend:    " + BACKEND_ENV);
console.log(" Dashboard:  " + DASHBOARD_ENV);
console.log("");
console.log(" Deployed contracts (Kite Testnet 2368):");
console.log("   IdentityRegistry    " + addrs.identity);
console.log("   ReputationRegistry  " + addrs.reputation);
console.log("   DealRecord          " + addrs.dealRecord);
console.log("");
