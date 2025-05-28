import httpx
from mcp.server.fastmcp import FastMCP
from github import GITHUB_TOKEN, create_github_headers
from handlers import register_handlers

# Create an MCP server
mcp = FastMCP("GitHubMCP")

# Register handlers
register_handlers(mcp)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')