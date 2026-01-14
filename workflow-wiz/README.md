# Workflow Wizard

A no-code / low-code AI agent that designs automations for real people. This system uses AI to understand user intent, plan workflows, validate them, and export them to various automation platforms.

## Architecture

The Workflow Wizard consists of four main agents:

1. **Intent Agent** - Understands what the user wants to automate
2. **Planner Agent** - Designs the workflow steps and tool integrations
3. **Validator Agent** - Ensures the workflow is feasible and optimized
4. **Exporter Agent** - Converts the workflow to various formats (n8n, Zapier, code, etc.)

## Features

- Natural language workflow creation
- Integration with popular tools:
  - Gmail (email automation)
  - Google Sheets (data management)
  - Notion (note-taking and databases)
  - Webhooks (custom integrations)
- Workflow validation and optimization
- Export to multiple formats

## Setup

### Prerequisites

- Python 3.9 or higher
- API keys for:
  - Anthropic (Claude AI)
  - Google Services (for Gmail, Sheets)
  - Notion (if using Notion integration)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

3. Run the application:
```bash
python app/run.py
```

Or use the API server:
```bash
python app/api.py
```

## Project Structure

```
workflow-wiz/
├── agents/           # AI agents for different workflow stages
│   ├── intent_agent.py
│   ├── planner_agent.py
│   ├── validator_agent.py
│   └── exporter_agent.py
├── app/             # Application entry points
│   ├── run.py       # CLI interface
│   └── api.py       # FastAPI server
├── tools/           # Tool integrations
│   ├── gmail.py
│   ├── sheets.py
│   ├── notion.py
│   └── webhook.py
├── prompts/         # Agent system prompts
├── schemas/         # JSON schemas for validation
└── evals/          # Evaluation configurations
```

## Usage

### CLI Mode

```bash
python app/run.py "Send me a daily email summary of my Google Sheets tasks"
```

### API Mode

```bash
# Start the server
uvicorn app.api:app --reload

# Make a request
curl -X POST http://localhost:8000/workflow \
  -H "Content-Type: application/json" \
  -d '{"description": "Send daily email summary of tasks"}'
```

## Development

Run tests:
```bash
pytest
```

Run evaluations:
```bash
# Run workflow evaluations
python -m pytest evals/ -v
```

## License

MIT
