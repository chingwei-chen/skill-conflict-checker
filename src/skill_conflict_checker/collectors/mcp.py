from __future__ import annotations

from skill_conflict_checker.models import SkillSource


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
        env_keys = list(cfg.get("env", {}).keys())
        content = (
            f"MCP server '{name}'\n"
            f"Command/URL: {cmd}\n"
            f"Args: {cfg.get('args', [])}\n"
            f"Exposed env keys: {env_keys}\n"
        )
        return SkillSource(
            name=f"mcp:{name}",
            source_type=self.source_type,
            source_path="settings.json[mcpServers]",
            description=f"MCP server providing external tools via {cmd or name}",
            content=content,
            metadata=cfg,
        )
