import httpx
from fastmcp import FastMCP
from github import GITHUB_TOKEN, create_github_headers

USER_ID = 1234567890

# Create FastMCP server
mcp = FastMCP(
    name="GitHubMCP",
    instructions="This server provides tools, resources and prompts to interact with the GitHub API.",
    include_tags={"public"},
    exclude_tags={"first_issue"}
)

sub_mcp = FastMCP(
    name="SubMCP",
)

@mcp.tool(
    tags={"public", "production"},
    exclude_args=["user_id"],   # user_id has to be injected by server, not provided by LLM
)
async def list_repository_issues(owner: str, repo_name: str, user_id: int = USER_ID) -> list[dict]:
    """
    Lists open issues for a given GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')

    Returns:
        list[dict]: A list of dictionaries, each containing information about an issue
    """
    # Limit to first 10 issues to avoid very long responses
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=open&per_page=10"
    print(f"Fetching issues from {api_url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            issues_data = response.json()
            
            if not issues_data:
                print("No open issues found for this repository.")
                return [{"message": "No open issues found for this repository."}]

            issues_summary = []
            for issue in issues_data:
                # Create a more concise summary
                summary = f"#{issue.get('number', 'N/A')}: {issue.get('title', 'No title')}"
                if issue.get('comments', 0) > 0:
                    summary += f" ({issue.get('comments')} comments)"
                
                issues_summary.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "user": issue.get("user", {}).get("login"),
                    "url": issue.get("html_url"),
                    "comments": issue.get("comments"),
                    "summary": summary
                })
            
            print(f"Found {len(issues_summary)} open issues.")
            
            # Add context information
            result = {
                "total_found": len(issues_summary),
                "repository": f"{owner}/{repo_name}",
                "note": "Showing first 10 open issues" if len(issues_summary) == 10 else f"Showing all {len(issues_summary)} open issues",
                "issues": issues_summary,
                "requested_by_user_id": user_id
            }
            
            return [result]
        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"
            
            print(f"GitHub API error: {e.response.status_code}. {error_message}")
            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return [{"error": f"An unexpected error occurred: {str(e)}"}]


@mcp.tool(tags={"private", "development"})
async def list_more_repository_issues(owner: str, repo_name: str) -> list[dict]:
    """
    Lists open issues for a given GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')

    Returns:
        list[dict]: A list of dictionaries, each containing information about an issue
    """
    # Limit to first 100 issues to avoid very long responses
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=open&per_page=100"
    print(f"Fetching issues from {api_url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            issues_data = response.json()
            
            if not issues_data:
                print("No open issues found for this repository.")
                return [{"message": "No open issues found for this repository."}]

            issues_summary = []
            for issue in issues_data:
                # Create a more concise summary
                summary = f"#{issue.get('number', 'N/A')}: {issue.get('title', 'No title')}"
                if issue.get('comments', 0) > 0:
                    summary += f" ({issue.get('comments')} comments)"
                
                issues_summary.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "user": issue.get("user", {}).get("login"),
                    "url": issue.get("html_url"),
                    "comments": issue.get("comments"),
                    "summary": summary
                })
            
            print(f"Found {len(issues_summary)} open issues.")
            
            # Add context information
            result = {
                "total_found": len(issues_summary),
                "repository": f"{owner}/{repo_name}",
                "note": "Showing first 10 open issues" if len(issues_summary) == 10 else f"Showing all {len(issues_summary)} open issues",
                "issues": issues_summary
            }
            
            return [result]
        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"
            
            print(f"GitHub API error: {e.response.status_code}. {error_message}")
            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return [{"error": f"An unexpected error occurred: {str(e)}"}]


@mcp.tool(tags={"public", "first_issue"})
async def first_repository_issue(owner: str, repo_name: str) -> list[dict]:
    """
    Gets the first issue ever created in a GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')

    Returns:
        list[dict]: A list containing information about the first issue created
    """
    # Get the first issue by sorting by creation date in ascending order
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=all&sort=created&direction=asc&per_page=1"
    print(f"Fetching first issue from {api_url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            issues_data = response.json()
            
            if not issues_data:
                print("No issues found for this repository.")
                return [{"message": "No issues found for this repository."}]

            first_issue = issues_data[0]
            
            # Create a detailed summary of the first issue
            summary = f"#{first_issue.get('number', 'N/A')}: {first_issue.get('title', 'No title')}"
            if first_issue.get('comments', 0) > 0:
                summary += f" ({first_issue.get('comments')} comments)"
            
            issue_info = {
                "number": first_issue.get("number"),
                "title": first_issue.get("title"),
                "user": first_issue.get("user", {}).get("login"),
                "url": first_issue.get("html_url"),
                "state": first_issue.get("state"),
                "comments": first_issue.get("comments"),
                "created_at": first_issue.get("created_at"),
                "updated_at": first_issue.get("updated_at"),
                "body": first_issue.get("body", "")[:500] + "..." if len(first_issue.get("body", "")) > 500 else first_issue.get("body", ""),
                "summary": summary
            }
            
            print(f"Found first issue: #{first_issue.get('number')} created on {first_issue.get('created_at')}")
            
            # Add context information
            result = {
                "repository": f"{owner}/{repo_name}",
                "note": "This is the very first issue created in this repository",
                "first_issue": issue_info
            }
            
            return [result]
            
        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"
            
            print(f"GitHub API error: {e.response.status_code}. {error_message}")
            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return [{"error": f"An unexpected error occurred: {str(e)}"}]


@sub_mcp.tool(tags={"public"})
def hello_world() -> str:
    """
    Returns a simple greeting.
    """
    return "Hello, world!"

mcp.mount("sub_mcp", sub_mcp)

if __name__ == "__main__":
    print("DEBUG: Starting FastMCP GitHub server...")
    print(f"DEBUG: Server name: {mcp.name}")
    
    # Initialize and run the server
    mcp.run(
        transport="stdio"
    )
