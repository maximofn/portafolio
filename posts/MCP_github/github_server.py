import httpx
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load the GitHub token from the .env file
load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Check if the GitHub token is configured
if not GITHUB_TOKEN:
    print("WARNING: The GITHUB_TOKEN environment variable is not configured.")
    print("Requests to the GitHub API may fail due to rate limits.")
    print("Create a .env file in this directory with GITHUB_TOKEN='your_token_here'")
    raise ValueError("GITHUB_TOKEN is not configured")

# Create an MCP server
mcp = FastMCP("GitHubMCP")

# Helper function to create headers for GitHub API requests
def create_github_headers():
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    # GitHub recommends including a User-Agent
    headers["User-Agent"] = "MCP_GitHub_Server_Example"
    headers["Accept"] = "application/vnd.github.v3+json" # Good practice
    return headers

# --- Resource: Get Repository Information ---
# This resource will fetch details about a specific GitHub repository
# It takes the owner of the repo and the repo name as parameters
# Example URI: github://repo/modelcontextprotocol/python-sdk
@mcp.resource("github://repo/{owner}/{repo_name}")
async def get_repository_info(owner: str, repo_name: str) -> dict:
    """
    Gets information about a GitHub repository, such as its description and stars.
    For example, to get info about 'modelcontextprotocol/python-sdk':
    owner='modelcontextprotocol', repo_name='python-sdk'
    """
    # Construct the URL for the GitHub API
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    
    # Use an async HTTP client to make the request
    async with httpx.AsyncClient() as client:
        try:
            # Make the GET request to the GitHub API with headers
            response = await client.get(api_url, headers=create_github_headers())
            # Raise an exception if the request failed (e.g., 404 Not Found)
            response.raise_for_status()
            # Parse the JSON response from the API
            repo_data = response.json()
            
            # Extract the information we want to return
            return {
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "open_issues": repo_data.get("open_issues_count"),
                "html_url": repo_data.get("html_url"),
                "debug": "debug_message"
            }
        except httpx.HTTPStatusError as e:
            # If there was an error from the API (like 403 Forbidden or 404 Not Found)
            # return an error message
            error_message = e.response.json().get("message", "No additional message from API.")
            # Add more context if it's a rate limit issue with a token
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"
                
            return {
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }
        except Exception as e:
            # For any other errors (network issues, etc.)
            return {"error": f"An unexpected error occurred: {str(e)}"}


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')