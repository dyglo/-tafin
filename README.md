# TAFIN

TAFIN (Think, Analyze, FINance) is an autonomous financial research agent that plans, executes, and validates multi-step market analysis. It decomposes complex questions into actionable tasks, gathers real-time financial statements, and synthesises data-backed answers—all from the command line.

<img width="979" height="651" alt="TAFIN screenshot" src="https://github.com/user-attachments/assets/5a2859d4-53cf-4638-998a-15cef3c98038" />

## Overview

TAFIN turns broad financial questions into clear research plans. It runs those plans using live market data, evaluates progress after each step, and iterates until it produces a confident response.

**Key capabilities**
- Task planning with guardrails against runaway loops
- Tool-assisted execution for financial data collection
- Automated self-validation of progress
- Access to income statements, balance sheets, and cash flow statements
- Concise, data-rich answers ready for follow-up analysis

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (`TAFIN_OPENAI_API_KEY` or `OPENAI_API_KEY`)
- Financial Datasets API key (`TAFIN_FINANCIAL_DATASETS_API_KEY` or `FINANCIAL_DATASETS_API_KEY`)
- *(Optional but recommended)* [uv](https://github.com/astral-sh/uv) package manager for fast virtualenv + dependency management

### 1. Clone the repository

```bash
git clone https://github.com/virattt/tafin.git
cd tafin
```

### 2. Install dependencies

**Option A – using uv (recommended)**
```bash
# Install uv if you do not already have it
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows PowerShell:
# iwr https://astral.sh/uv/install.ps1 -useb | iex

uv sync
```

**Option B – using pip**
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

python -m pip install -e .
```

### 3. Configure API keys

```bash
cp env.example .env

# Edit .env and set your credentials
# TAFIN_OPENAI_API_KEY=your-openai-api-key
# TAFIN_FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
# TAFIN_SERPER_API_KEY=your-serper-api-key
# TAFIN_ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
```

### 4. Run TAFIN

```bash
# With uv (either command works)
uv run tafin
uv run tafin-agent

# Without uv (after pip install -e .)
python -m tafin.cli
```

If an OpenAI key is not configured, TAFIN automatically falls back to a **search-only mode** powered by Serper and Alpha Vantage so you can still gather market context.

From there, use the `tafin>` prompt to ask questions such as:
- What was Apple's revenue growth over the last four quarters?
- Compare Microsoft and Google's operating margins for 2023.
- Analyse Tesla's cash flow trends over the past year.
- What is Amazon's debt-to-equity ratio based on recent financials?

TAFIN will:
1. Break down the query into structured tasks
2. Call the right tools to gather data
3. Validate progress after each step
4. Present a concise answer with the key numbers

## Architecture

TAFIN uses a modular agent stack:

- **Planning agent**: analyses the query and produces task lists
- **Action agent**: decides which tool to run next
- **Validation agent**: checks whether the current task is complete
- **Answer agent**: composes the final response from collected outputs

## Project Structure

```
tafin/
├── src/
│   └── tafin/
│       ├── agent.py      # Main agent orchestration logic
│       ├── model.py      # LLM interface (OpenAI gpt-4o)
│       ├── tools.py      # Financial Datasets API helpers
│       ├── prompts.py    # System prompts for each component
│       ├── schemas.py    # Pydantic models used across agents
│       ├── cli.py        # CLI entry point
│       └── utils/        # Logging, UI, intro banner
├── pyproject.toml
├── package.json
├── index.js
├── env.example
└── uv.lock
```

## Configuration

The `Agent` class can be tuned to suit your workflow:

```python
from tafin.agent import Agent

agent = Agent(
    max_steps=20,              # Global safety limit
    max_steps_per_task=5       # Per-task iteration limit
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a pull request

Please keep pull requests focused to simplify reviews.

## License

This project is licensed under the MIT License.
