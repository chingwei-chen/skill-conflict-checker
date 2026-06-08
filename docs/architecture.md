# Architecture

## Overview

`skill-conflict-checker` follows SOLID OOP principles with a layered pipeline:

```
CLI (click)
  └─ ConflictChecker (orchestrator)
       ├─ [AbstractCollector] × N  →  list[SkillSource]
       ├─ AbstractAnalyzer          →  list[Conflict]
       └─ [AbstractReporter] × N
```

## Layers

### Models (`models/`)
Pure data classes; no behaviour.

| Class | Purpose |
|---|---|
| `SkillSource` | One rule-bearing source (skill, plugin, MCP entry, CLAUDE.md) |
| `Conflict` | A detected rule conflict with severity, category, and recommendation |
| `Severity` | Enum: `HIGH` / `MEDIUM` / `LOW` |

### Collectors (`collectors/`)
Each collector has **one responsibility**: read one source category and return `list[SkillSource]`.

| Class | Source |
|---|---|
| `UserSkillCollector` | `~/.claude/skills/*/SKILL.md` |
| `PluginSkillCollector` | `~/.claude/plugins/cache/**/skills/*/SKILL.md` |
| `McpCollector` | `settings.json → mcpServers` |
| `ClaudeMdCollector` | `~/.claude/CLAUDE.md` |

All implement `AbstractCollector` (a `typing.Protocol`). New source types extend the Protocol without touching existing code (Open/Closed).

### Analyzers (`analyzers/`)
`ClaudeAnalyzer` sends all sources to Claude API (claude-opus-4-8, adaptive thinking, streaming) and parses JSON conflicts from the response.

The `AbstractAnalyzer` Protocol decouples the orchestrator from any LLM provider.

### Reporters (`reporters/`)
Each reporter renders `list[Conflict]` in one output format.

| Class | Format |
|---|---|
| `ConsoleReporter` | Rich terminal panels + summary table |
| `JsonReporter` | JSON file or stdout |
| `MarkdownReporter` | Markdown file |

### Orchestrator (`checker.py`)
`ConflictChecker` receives all collaborators via constructor (Dependency Inversion). It:
1. Calls each collector's `.collect()`
2. Passes the combined sources to the analyzer
3. Passes conflicts to each reporter

### CLI (`cli.py`)
Click entry point. Wires concrete implementations and calls `ConflictChecker.run()`.

## SOLID Mapping

| Principle | Where applied |
|---|---|
| **S** — Single Responsibility | Each collector handles exactly one source type; reporters each handle one format |
| **O** — Open/Closed | New collectors/reporters via Protocol, no existing code changes |
| **L** — Liskov Substitution | Any `AbstractCollector` impl can replace another |
| **I** — Interface Segregation | Collector Protocol has 2 methods; Analyzer has 1; Reporter has 1 |
| **D** — Dependency Inversion | `ConflictChecker` depends on Protocols, not concrete classes |
