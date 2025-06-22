import httpx
from fastmcp import FastMCP
from github import GITHUB_TOKEN, create_github_headers

# Create a FastMCP server
mcp = FastMCP("GitHubMCP")

@mcp.resource("github://repo/{owner}/{repo_name}")
async def get_repository_info(owner: str, repo_name: str) -> dict:
    """
    Gets detailed information for a given GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')

    Returns:
        dict: A dictionary containing repository details.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    print(f"Fetching repository info from {api_url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            repo_data = response.json()
            
            # Return the data as a dictionary with repository information
            return {
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "open_issues": repo_data.get("open_issues_count"),
                "language": repo_data.get("language"),
                "url": repo_data.get("html_url"),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "size": repo_data.get("size"),
                "watchers": repo_data.get("watchers_count"),
                "default_branch": repo_data.get("default_branch"),
                "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                "owner": repo_data.get("owner", {}).get("login"),
                "owner_type": repo_data.get("owner", {}).get("type"),
                "homepage": repo_data.get("homepage"),
                "topics": repo_data.get("topics", [])
            }

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"
            
            print(f"GitHub API error: {e.response.status_code}. {error_message}")
            return {
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def list_repository_issues(owner: str, repo_name: str) -> list[dict]:
    """
    Lists open issues for a given GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')

    Returns:
        list[dict]: A list of dictionaries, each containing information about an issue
    """
    # Limitar a los primeros 10 issues para evitar respuestas muy largas
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
                summary = f"#{issue.get('number', 'N/A')}: {issue.get('title', 'Sin título')}"
                if issue.get('comments', 0) > 0:
                    summary += f" ({issue.get('comments')} comentarios)"
                
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
                "note": "Mostrando los primeros 10 issues abiertos" if len(issues_summary) == 10 else f"Mostrando todos los {len(issues_summary)} issues abiertos",
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


if __name__ == "__main__":
    print("DEBUG: Starting GitHub FastMCP server...")
    print(f"DEBUG: Server name: {mcp.name}")
    print("DEBUG: Available tools: list_repository_issues")
    print("DEBUG: Available resources: github://repo/{owner}/{repo_name}")
    
    # Initialize and run the server
    mcp.run() 