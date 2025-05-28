import httpx
from mcp.server.fastmcp import FastMCP, Image
from github import GITHUB_TOKEN, create_github_headers
from handlers import register_handlers
from PIL import Image as PILImage

# Create an MCP server
mcp = FastMCP("GitHubMCP")

# Register handlers
register_handlers(mcp)

# --- Tool: List Repository Issues ---
# This tool will list open issues for a specific GitHub repository
# It takes the owner and repo name as parameters
@mcp.tool()
async def list_repository_issues(owner: str, repo_name: str) -> list[dict]:
    """
    Lists open issues for a given GitHub repository.
    owner: The owner of the repository (e.g., 'modelcontextprotocol')
    repo_name: The name of the repository (e.g., 'python-sdk')
    """
    # Construct the URL for the GitHub API endpoint for issues
    # We'll filter by 'open' state
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=open"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            issues_data = response.json()
            
            # Extract relevant information for each issue
            issues_summary = []
            if not issues_data: # Handle case where there are no issues
                return [{"message": "No open issues found for this repository."}]

            for issue in issues_data:
                issues_summary.append({
                    "title": issue.get("title"),
                    "number": issue.get("number"),
                    "user": issue.get("user", {}).get("login"),
                    "url": issue.get("html_url"),
                    "comments": issue.get("comments")
                })
            return issues_summary
        except httpx.HTTPStatusError as e:
            # Return a list with an error dictionary if something goes wrong
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"

            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            return [{"error": f"An unexpected error occurred: {str(e)}"}]

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')