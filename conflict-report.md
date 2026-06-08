# Skill Conflict Report

**Sources scanned:** 51  
**Conflicts found:** 9

## 🔴 HIGH Severity

### ctx-stats: terse 2-3 lines vs mandatory full verbatim copy
- **Category:** response_style
- **Sources:** `ctx-stats [skill]` ↔ `ctx-stats [plugin_skill]`

Local ctx-stats skill explicitly forbids copy-pasting full tables and mandates 2-3 line ultra-terse output ('Numbers only, ultra-terse'). Plugin ctx-stats skill has opposite mandate: 'CRITICAL: You MUST copy-paste the ENTIRE tool output... Do NOT summarize, do NOT collapse, do NOT paraphrase.' Both fire on /ctx-stats, producing directly contradictory output behavior.

**Recommendation:** Remove local ctx-stats skill entirely. Plugin version has more complete output contract and is the authoritative source. Redirect /ctx-stats to /context-mode:ctx-stats.

---

### Caveman full mode (English-pattern) vs mandatory Traditional Chinese output
- **Category:** language
- **Sources:** `caveman [skill]` ↔ `CLAUDE.md (global instructions)`

CLAUDE.md (global) mandates '一律使用繁體中文台灣用語產生對話及結果' for all responses. The caveman skill at 'full' level (active via SessionStart hook) instructs English-style compression with English examples as canonical. Default full mode produces English-pattern output directly conflicting with the Traditional Chinese requirement. Wenyan variants exist but are not the default.

**Recommendation:** Change caveman default mode to 'wenyan-full' in ~/.config/caveman/config.json or set CAVEMAN_DEFAULT_MODE=wenyan-full so compression respects the zh-TW mandate. Alternatively add explicit note in caveman skill: 'When session language is zh-TW, use wenyan variant by default.'

---

### Two PR-creation skills with conflicting body templates and workflows
- **Category:** trigger_overlap
- **Sources:** `commit-and-pr [skill]` ↔ `github-pr [skill]`

Both commit-and-pr and github-pr handle PR creation with 'develop' as default target but produce incompatible output. commit-and-pr generates a 3-section body (Summary/Test plan/attribution). github-pr generates a complex multi-section body (Jira links, file categorization by path pattern, QA Test scenarios, Test plan with migration steps). No priority rule determines which fires. Invoking both in one session produces inconsistent PRs.

**Recommendation:** Designate github-pr as the canonical PR skill for this project (it has the richer template). Deprecate or rename commit-and-pr to a lightweight alias that delegates to github-pr, or scope commit-and-pr to non-CF projects only.

---

## 🟡 MEDIUM Severity

### CLI-first global rule vs context-mode default-to-sandbox rule
- **Category:** tool_usage
- **Sources:** `CLAUDE.md (global instructions)` ↔ `context-mode [plugin_skill]`

CLAUDE.md (global) states '最高優先序是使用內建的 CLI 工具' — highest priority is built-in CLI tools, implying Bash/shell-first execution. context-mode plugin skill states 'Default to context-mode for ALL commands. Only use Bash for guaranteed-small-output operations', routing most work through ctx_execute instead of Bash. These create opposite default tool preferences.

**Recommendation:** Clarify in CLAUDE.md that 'CLI-first' means prefer CLI over GUI/web interfaces, while context-mode sandbox routing is a performance layer wrapping CLI calls. Add note: 'CLI calls that produce large output must be routed through ctx_execute per context-mode rules.'

---

### Duplicate Jira MCP servers cause ambiguous backend detection
- **Category:** tool_usage
- **Sources:** `mcp:atlassian [mcp]` ↔ `mcp:jira [mcp]`

Both mcp:atlassian (remote SSE at mcp.atlassian.com) and mcp:jira (local uvx mcp-atlassian with hardcoded credentials) are registered. The jira skill backend detection checks for 'mcp__atlassian__* tools' and will match tools from both servers. This leads to ambiguous tool selection, potential duplicate calls, and credential confusion (one server has credentials in env vars, the other authenticates via SSE).

**Recommendation:** Remove mcp:atlassian. mcp:jira (local uvx with explicit JIRA_URL and credentials) is self-contained and sufficient. Update jira skill backend detection to name 'mcp:jira' explicitly rather than detecting any mcp__atlassian__* tools.

---

### caveman-commit uses English-only examples, no zh-TW directive
- **Category:** language
- **Sources:** `caveman-commit [skill]` ↔ `github-pr [skill]`

CLAUDE.md (global) and both github-pr and commit-and-pr skills explicitly mandate Traditional Chinese commit descriptions ('繁體中文描述'). caveman-commit specifies Conventional Commits format with English-only examples and no language directive. When caveman-commit is active, it overrides the zh-TW commit convention established by the other two skills.

**Recommendation:** Add explicit language directive to caveman-commit: 'Subject description in Traditional Chinese (zh-TW) per project convention; type/scope tokens remain ASCII.' This aligns caveman-commit with github-pr and commit-and-pr without changing the Conventional Commits structure.

---

### caveman-compress runs raw python3, violating uv/uvx mandate
- **Category:** tool_usage
- **Sources:** `CLAUDE.md (global instructions)` ↔ `caveman-compress [skill]`

CLAUDE.md (global) prohibits native Python environment: '嚴禁使用 pip 安裝軟體，一律使用 uv 建立虛擬環境，不允許使用原生 Python 環境'. The caveman-compress skill instructs running 'python3 -m scripts <filepath>' directly using the native python3 binary, bypassing uv entirely.

**Recommendation:** Update caveman-compress process step 2 to: 'uv run python3 -m scripts <absolute_filepath>' or prepend a uv venv activation step. Alternatively add a pyproject.toml to scripts/ and use 'uvx --from . scripts <filepath>' so it is self-contained.

---

### DB credentials hardcoded in skill content vs no-credential-paste rule
- **Category:** other
- **Sources:** `CLAUDE.md (global instructions)` ↔ `local-cf-db [skill]`

CLAUDE.md (global) prohibits pasting credentials in any conversation: '不允許直接貼出密碼、金鑰、Access Token、API Key 等機密資料'. local-cf-db skill hardcodes 'Password: dev' and the full connection string 'mysql -h127.0.0.1 -P3306 -uroot -pdev' inline. When this skill loads into context, the password is directly visible and will appear in responses that cite the skill.

**Recommendation:** Replace hardcoded '-pdev' with '${CF_DB_PASSWORD:-dev}' and note the env var name. Store the literal 'dev' value in a local .env file. The skill should reference the variable name, not the value, keeping it compliant even for dev credentials.

---

## 🟢 LOW Severity

### Seven caveman skills registered in both local skills dir and plugin cache
- **Category:** priority
- **Sources:** `caveman [skill]` ↔ `caveman [plugin_skill]`

caveman, caveman-help, caveman-review, caveman-compress, cavecrew, caveman-stats, and caveman-commit each exist identically under ~/.claude/skills/ and ~/.claude/plugins/cache/caveman/. No priority rule resolves which copy fires on a trigger. If content diverges across plugin updates, the stale local copy silently wins or both fire causing double-execution.

**Recommendation:** Delete all seven local copies under ~/.claude/skills/ and rely solely on the plugin cache versions. The plugin mechanism handles versioning and updates; local copies create maintenance split-brain.

---
