# Lead Nurture Agent

A 3-layer AI orchestration system for lead nurturing, built on a deterministic execution architecture.

## Architecture Overview

This system uses a 3-layer approach to separate concerns and maximize reliability:

### Layer 1: Directives (What to do)
- **Location**: `directives/`
- Natural language SOPs in Markdown
- Define goals, inputs, tools, outputs, and edge cases
- Living documents that improve over time

### Layer 2: Orchestration (Decision making)
- **Layer**: Claude AI
- Reads directives and makes intelligent routing decisions
- Calls execution tools in the right order
- Handles errors and updates directives with learnings

### Layer 3: Execution (Doing the work)
- **Location**: `execution/`
- Deterministic Python scripts
- Handles API calls, data processing, file operations
- Reliable, testable, fast

## Directory Structure

```
Lead Nurture/
├── .tmp/                  # Temporary/intermediate files (never commit)
├── directives/            # Markdown SOPs (the instruction set)
├── execution/             # Python scripts (the tools)
│   ├── webhooks.json     # Webhook configuration
│   └── *.py              # Execution scripts
├── .env                   # Environment variables (never commit)
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Agent instructions
└── README.md             # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install python-dotenv anthropic openai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client modal
```

### 2. Configure Environment Variables

Edit [.env](.env) and add your API keys:

```bash
# Required for Claude orchestration
ANTHROPIC_API_KEY=your_anthropic_key_here

# Add other keys as needed
OPENAI_API_KEY=your_openai_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### 3. Google Sheets Setup (if needed)

1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create OAuth 2.0 credentials
5. Download and save as `credentials.json` in this directory
6. First run will generate `token.json`

### 4. Modal Setup (for webhooks)

```bash
# Install Modal
pip install modal

# Authenticate
modal token new

# Deploy webhooks
modal deploy execution/modal_webhook.py
```

## Usage

### Creating Directives

1. Create a new `.md` file in `directives/`
2. Include: Goal, Inputs, Tools/Scripts, Outputs, Edge Cases
3. Reference it from orchestration layer

### Creating Execution Scripts

1. Create a new `.py` file in `execution/`
2. Make it deterministic and testable
3. Use environment variables for credentials
4. Document in the corresponding directive

### Adding Webhooks

See `directives/add_webhook.md` for complete instructions.

## Key Principles

1. **Check for tools first** - Before writing code, check `execution/` directory
2. **Self-anneal when things break** - Fix errors, update tools, update directives
3. **Update directives as you learn** - Keep documentation current
4. **Local files are temporary** - Deliverables live in cloud (Google Sheets, Slides)

## File Organization

- **Deliverables**: Cloud-based (Google Sheets, Slides) - user-accessible
- **Intermediates**: `.tmp/` directory - regenerated as needed, never committed

## Available Tools

Webhook endpoints have access to:
- `send_email` - Send email notifications
- `read_sheet` - Read from Google Sheets
- `update_sheet` - Update Google Sheets

## Self-Annealing Loop

When errors occur:
1. Read error message and stack trace
2. Fix the script and test
3. Update the directive with learnings
4. System is now stronger

## Getting Started

1. Review [CLAUDE.md](CLAUDE.md) for complete agent instructions
2. Create your first directive in `directives/`
3. Build corresponding execution script in `execution/`
4. Test and iterate

## Notes

- This system is designed to be reliable and self-improving
- LLMs handle decision-making, Python handles execution
- Everything in `.tmp/` can be deleted and regenerated
- Directives are living documents - update them as you learn
