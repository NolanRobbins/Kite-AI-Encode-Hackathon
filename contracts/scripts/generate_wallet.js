// One-shot throwaway-wallet generator for the Kite testnet hackathon deploy.
// Writes the private key directly into ./.env (gitignored). Prints ONLY the
// public address so the key never enters terminal logs or chat transcripts.
//
// Usage:  node scripts/generate_wallet.js
//
// If contracts/.env already contains a PRIVATE_KEY, this script refuses to
// overwrite it (run with `--force` to override that guard).

const fs = require("fs");
const path = require("path");
const { Wallet } = require("ethers");

const ENV_PATH = path.resolve(__dirname, "..", ".env");
const FORCE = process.argv.includes("--force");

function readExisting() {
  if (!fs.existsSync(ENV_PATH)) return null;
  return fs.readFileSync(ENV_PATH, "utf8");
}

function hasRealKey(contents) {
  if (!contents) return false;
  const match = contents.match(/^PRIVATE_KEY\s*=\s*(\S+)/m);
  if (!match) return false;
  const v = match[1];
  if (!v || v.startsWith("0x...") || v === "0x") return false;
  return true;
}

const existing = readExisting();
if (hasRealKey(existing) && !FORCE) {
  console.error(
    "contracts/.env already contains a PRIVATE_KEY. Refusing to overwrite.\n" +
      "Pass --force to override (your old wallet will be unrecoverable from this file)."
  );
  process.exit(1);
}

const wallet = Wallet.createRandom();

const body =
  "# === Kite Testnet Deployment ===\n" +
  "# Generated " +
  new Date().toISOString() +
  " by scripts/generate_wallet.js\n" +
  "# Disposable throwaway wallet for hackathon deploys only.\n" +
  "# Chain: Kite Testnet (Chain ID 2368, RPC https://rpc-testnet.gokite.ai/)\n" +
  "# Faucet (free testnet KITE): https://faucet.gokite.ai\n" +
  "PRIVATE_KEY=" +
  wallet.privateKey +
  "\n";

fs.writeFileSync(ENV_PATH, body, { mode: 0o600 });

console.log("");
console.log("================================================================");
console.log(" Throwaway Kite testnet wallet generated.");
console.log("================================================================");
console.log("");
console.log(" Public address:  " + wallet.address);
console.log("");
console.log(" Private key:     written to contracts/.env (gitignored).");
console.log("");
console.log(" NEXT STEP:");
console.log(" 1. Open https://faucet.gokite.ai");
console.log(" 2. Paste the address above");
console.log(' 3. Request testnet KITE (free, ~0.5 KITE/day)');
console.log(" 4. Come back here and confirm faucet succeeded");
console.log("");
