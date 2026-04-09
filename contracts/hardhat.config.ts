import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@nomicfoundation/hardhat-verify";
import "@nomicfoundation/hardhat-ignition-ethers";
import * as dotenv from "dotenv";
dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.26",
    settings: {
      evmVersion: "cancun",
      viaIR: true,
      optimizer: { enabled: true, runs: 200 },
    },
  },
  paths: {
    sources: "./src",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  networks: {
    kiteTestnet: {
      url: "https://rpc-testnet.gokite.ai/",
      chainId: 2368,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
  etherscan: {
    apiKey: {
      kiteTestnet: "no-api-key-needed",
    },
    customChains: [
      {
        network: "kiteTestnet",
        chainId: 2368,
        urls: {
          apiURL: "https://testnet.kitescan.ai/api",
          browserURL: "https://testnet.kitescan.ai",
        },
      },
    ],
  },
  sourcify: {
    enabled: true,
  },
};

export default config;
