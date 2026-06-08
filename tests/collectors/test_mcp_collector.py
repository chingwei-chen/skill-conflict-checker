from skill_conflict_checker.collectors.mcp import McpCollector


def test_collect_mcp_servers():
    mcp = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            "env": {},
        },
        "redis": {
            "url": "redis://localhost:6379",
            "env": {"REDIS_PASSWORD": "xxx"},
        },
    }
    collector = McpCollector(mcp)
    sources = collector.collect()
    assert len(sources) == 2
    names = {s.name for s in sources}
    assert "mcp:filesystem" in names
    assert "mcp:redis" in names


def test_collect_empty():
    collector = McpCollector({})
    assert collector.collect() == []


def test_source_type():
    collector = McpCollector({})
    assert collector.source_type == "mcp"


def test_mcp_content_includes_command():
    mcp = {"myserver": {"command": "python3", "args": ["-m", "myserver"]}}
    collector = McpCollector(mcp)
    sources = collector.collect()
    assert "python3" in sources[0].content
