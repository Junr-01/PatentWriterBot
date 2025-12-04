import asyncio
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

# 获取项目根目录（tools.py 位于 agent/utils/，向上两级到项目根目录）
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_MCP_SERVER_DIR = _PROJECT_ROOT / "mcp_server"

_client = MultiServerMCPClient(
    {
        "filesystem": {
            "command": "python",
            "args": [
                str(_MCP_SERVER_DIR / "filesystem.py"),
            ],
            "transport": "stdio",
        },
        "markitdown": {
            "command": "markitdown-mcp",
            "args": [],
            "transport": "stdio",
        },
        "google_patent_search": {
            "command": "python",
            "args": [
                str(_MCP_SERVER_DIR / "google_patent_search.py"),
            ],
            "env": {
                "SERPAPI_API_KEY": os.getenv("SERPAPI_API_KEY")
            },
            "transport": "stdio"
        },
        "learn_skills": {
            "command": "python",
            "args": [
                str(_MCP_SERVER_DIR / "skills.py"),
            ],
            "transport": "stdio",
        },
    }
)

async def aget_filesystem_tools():
    filesystem_tools = await _client.get_tools(server_name="filesystem")
    return filesystem_tools

def get_filesystem_tools():
    return asyncio.run(aget_filesystem_tools())

async def aget_markitdown_tools():
    markitdown_tools = await _client.get_tools(server_name="markitdown")
    return markitdown_tools

def get_markitdown_tools():
    return asyncio.run(aget_markitdown_tools())

async def aget_google_patent_search_tools():
    google_patent_search_tools = await _client.get_tools(server_name="google_patent_search")
    return google_patent_search_tools

def get_google_patent_search_tools():
    return asyncio.run(aget_google_patent_search_tools())

async def aget_learn_skills_tools():
    learn_skills = await _client.get_tools(server_name="learn_skills")
    return learn_skills

def get_learn_skills_tools():
    return asyncio.run(aget_learn_skills_tools())

if __name__ == "__main__":
    ...