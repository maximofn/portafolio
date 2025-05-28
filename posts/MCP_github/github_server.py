from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("GitHubMCP")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')