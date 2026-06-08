from __future__ import annotations

import re

from skill_conflict_checker.models import SkillSource

_SECRET_KEYS = re.compile(
    r"(key|token|secret|password|passwd|credential|auth|api_key|access_key)",
    re.IGNORECASE,
)


def _mask_env(env: dict) -> dict:
    return {
        k: ("***" if _SECRET_KEYS.search(k) else v)
        for k, v in env.items()
    }


class McpCollector:
    """Converts MCP server configurations into SkillSource entries."""

    def __init__(self, mcp_servers: dict) -> None:
        self._mcp_servers = mcp_servers

    @property
    def source_type(self) -> str:
        return "mcp"

    def collect(self) -> list[SkillSource]:
        sources: list[SkillSource] = []
        for name, cfg in self._mcp_servers.items():
            sources.append(self._build(name, cfg))
        return sources

    def _build(self, name: str, cfg: dict) -> SkillSource:
        cmd = cfg.get("command", cfg.get("url", ""))
        masked_env = _mask_env(cfg.get("env", {}))
        content = (
            f"MCP server '{name}'\n"
            f"Command/URL: {cmd}\n"
            f"Args: {cfg.get('args', [])}\n"
            f"Env: {masked_env}\n"
        )
        safe_cfg = {**cfg, "env": masked_env}
        return SkillSource(
            name=f"mcp:{name}",
            source_type=self.source_type,
            source_path="settings.json[mcpServers]",
            description=f"MCP server providing external tools via {cmd or name}",
            content=content,
            metadata=safe_cfg,
        )
