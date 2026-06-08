# Conflict Types

Claude API detects the following conflict categories:

## `response_style`
Rules that dictate how Claude formats or structures its output contradict each other.

**Example:** One skill says "always provide detailed step-by-step explanations" while another (like caveman-mode) says "use fragments, drop filler words."

## `trigger_overlap`
Two or more skills activate under the same conditions but give different instructions.

**Example:** Both a "code-review" skill and a "debugging" skill trigger when the user shares Python code, but one says "focus on security" and the other says "focus on performance."

## `tool_usage`
Tool availability or usage policies conflict.

**Example:** CLAUDE.md disables web search globally, but a research skill explicitly enables and relies on it.

## `persistence`
Memory and context persistence behaviours conflict.

**Example:** One skill says "always remember user preferences across sessions" while the global config says "never store user data."

## `language`
Language or locale requirements contradict.

**Example:** CLAUDE.md specifies Traditional Chinese (Taiwan) output, but a skill specifies English-only responses.

## `priority`
Ordering or priority declarations conflict.

**Example:** Two skills both claim to have the highest priority, creating an ambiguous execution order.

## `other`
Any conflict that doesn't fit the above categories.

---

## Severity Levels

| Level | Meaning |
|---|---|
| `HIGH` | Rules directly contradict — behaviour is unpredictable in affected scenarios |
| `MEDIUM` | Rules partially overlap — behaviour may be inconsistent depending on context |
| `LOW` | Rules could create subtle friction — usually resolvable with a small tweak |
