# Contributing to NegotiatorGrid

Thank you for your interest in contributing to NegotiatorGrid! This document provides guidelines and instructions for contributing.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+ (for smart contracts and dashboard)
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/NolanRobbins/Kite-AI-Encode-Hackathon.git
cd Kite-AI-Encode-Hackathon

# Install Python dependencies (with dev extras)
pip install -e ".[dev]"

# Optional: install gambit for Nash equilibrium computation
pip install -e ".[dev,gambit]"

# Set up environment variables
cp .env.example .env
# Edit .env with your values

# Install smart contract dependencies
cd contracts
npm install
cd ..

# Install dashboard dependencies
cd dashboard
npm install
cd ..
```

### Verify Your Setup

```bash
# Run Python tests
pytest tests/

# Run Solidity tests
cd contracts && npx hardhat test

# Run the demo
python demo.py
```

---

## Code Style

### Python

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

Configuration is in `pyproject.toml`:
- Line length: 100
- Target: Python 3.11
- Rules: `E` (pycodestyle errors), `F` (pyflakes), `I` (isort), `W` (pycodestyle warnings)

### Solidity

- Solidity 0.8.26
- Follow the existing contract patterns in `contracts/src/`

---

## Making Changes

### Branch Naming

```
feature/short-description    # New features
fix/short-description        # Bug fixes
docs/short-description       # Documentation updates
```

### Commit Messages

Write clear, concise commit messages:

```
feat: add opponent model confidence scoring
fix: correct Nash equilibrium validation for edge case
docs: update README with deployment instructions
test: add integration test for attestation pipeline
```

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. Make your changes with appropriate tests.
3. Ensure all tests pass (`pytest tests/` and `cd contracts && npx hardhat test`).
4. Ensure code passes linting (`ruff check .`).
5. Write a clear PR description explaining what changed and why.

---

## Test Requirements

All contributions must include tests for new functionality:

- **Python**: Add tests to `tests/` using pytest. Use `pytest-asyncio` for async tests.
- **Solidity**: Add tests to `contracts/test/` using Hardhat.

```bash
# Run all Python tests with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_negotiation.py -v

# Run Solidity tests
cd contracts && npx hardhat test
```

---

## Project Structure

See [README.md](README.md#project-structure) for the full project structure. Key areas for contributions:

| Area | Directory | Description |
|------|-----------|-------------|
| Negotiation engine | `negotiatorgrid/core/` | NegMAS integration, opponent modeling, Nash guardrail |
| Smart contracts | `contracts/src/` | DealRecord, IdentityRegistry, ReputationRegistry |
| API layer | `negotiatorgrid/api/` | FastAPI endpoints and WebSocket |
| LLM integration | `negotiatorgrid/llm/` | Natural language offer generation |
| Dashboard | `dashboard/` | Next.js frontend |
| Tests | `tests/` | Python test suite |

---

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests.
- For security vulnerabilities, see [SECURITY.md](SECURITY.md) — do not open public issues.
- Include steps to reproduce for bug reports.

---

## License

By contributing to NegotiatorGrid, you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).
