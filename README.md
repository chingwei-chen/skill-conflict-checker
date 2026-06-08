# skill-conflict-checker

A CLI tool that scans all active Claude Code skills, plugin skills, MCP server configurations, and global `CLAUDE.md` instructions, then uses the Claude API to detect rule conflicts between them.

## Features

- Detects conflicts across response style, tool usage, language, persistence, and priority rules
- Supports multiple output formats: Rich terminal, JSON, Markdown
- SOLID OOP architecture — each collector, analyzer, and reporter is independently extensible
- Uses `claude-opus-4-8` with adaptive thinking for deep conflict analysis

## Installation

```bash
# Clone and install in a uv virtual environment
git clone https://github.com/f1291883652/skill-conflict-checker.git
cd skill-conflict-checker
uv sync
```

Set your API key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or create a .env file:
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Usage

```bash
# Basic scan (Rich terminal output)
uv run skill-conflict-checker

# JSON output to file
uv run skill-conflict-checker --format json --output conflicts.json

# Markdown report
uv run skill-conflict-checker --format markdown --output report.md

# Scan only skills and CLAUDE.md (skip plugins and MCP)
uv run skill-conflict-checker --no-plugins --no-mcp

# Custom .claude directory
uv run skill-conflict-checker --claude-dir /path/to/.claude

# Use a different model
uv run skill-conflict-checker --model claude-opus-4-8
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | No conflicts found |
| `1` | One or more conflicts detected |
| `2` | Runtime error (API failure, config error) |

## Options

```
--claude-dir PATH        Path to .claude directory (default: ~/.claude)
--format [console|json|markdown]  Output format (default: console)
--output, -o PATH        Output file path (required for markdown)
--model TEXT             Claude model to use (default: claude-opus-4-8)
--no-skills              Skip user skill collection
--no-plugins             Skip plugin skill collection
--no-mcp                 Skip MCP server collection
--no-claude-md           Skip CLAUDE.md collection
--help                   Show this message and exit
```

## Development

```bash
# Install with dev dependencies
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=skill_conflict_checker --cov-report=term-missing
```

## Project Structure

```
skill-conflict-checker/
├── src/skill_conflict_checker/
│   ├── models/           # Data classes (SkillSource, Conflict, Severity)
│   ├── collectors/       # One collector per source type (SOLID SRP)
│   ├── analyzers/        # Claude API conflict detection
│   ├── reporters/        # Console, JSON, Markdown output
│   ├── checker.py        # Orchestrator with dependency injection
│   └── cli.py            # Click entry point
├── tests/
│   ├── collectors/
│   ├── analyzers/
│   └── reporters/
└── docs/
    ├── architecture.md   # SOLID design rationale
    └── conflict-types.md # Conflict category reference
```

See [docs/architecture.md](docs/architecture.md) for the full SOLID design rationale and [docs/conflict-types.md](docs/conflict-types.md) for conflict category definitions.

## License

MIT
