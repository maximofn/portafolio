import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP, Image, Context
from github import GITHUB_TOKEN, create_github_headers
import anyio
from datetime import datetime

# Create an MCP server
mcp = FastMCP("GitHubMCP")

@mcp.prompt()
def generate_analysis_request(owner: str, repo_name: str) -> str:
    """Generate a prompt asking for repository analysis."""
    return f"""Please analyze the GitHub repository {owner}/{repo_name}. 

First, gather information about:
1. Repository details (stars, forks, description, language)
2. Current open issues
3. Recent activity patterns

Then provide analysis covering:
- Repository health assessment
- Issue patterns and trends  
- Community engagement
- Strategic recommendations
- Technical insights

Structure your response with clear headings and actionable insights."""

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
            
            return {
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "open_issues": repo_data.get("open_issues_count"),
                "language": repo_data.get("language"),
                "url": repo_data.get("html_url")
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
async def list_repository_issues(owner: str, repo_name: str, ctx: Context) -> list[dict]:
    """
    Lists open issues for a given GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')
        ctx: The MCP context for logging.

    Returns:
        list[dict]: A list of dictionaries, each containing information about an issue
    """
    # Limitar a los primeros 10 issues para evitar respuestas muy largas
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=open&per_page=10"
    await ctx.info(f"Fetching issues from {api_url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            issues_data = response.json()
            
            if not issues_data:
                await ctx.info("No open issues found for this repository.")
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
            
            await ctx.info(f"Found {len(issues_summary)} open issues.")
            
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
            
            await ctx.info(f"GitHub API error: {e.response.status_code}. {error_message}")
            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            await ctx.info(f"An unexpected error occurred: {str(e)}")
            return [{"error": f"An unexpected error occurred: {str(e)}"}]

@mcp.tool()
async def get_repository_image(owner: str, ctx: Context) -> Optional[Image]:
    """
    Get the image of a github profile.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        ctx: The MCP context for logging.

    Returns:
        Optional[Image]: The Image object if successful, otherwise None.
    """
    api_url = f"https://api.github.com/users/{owner}"
    await ctx.info(f"Fetching user data for '{owner}' from {api_url}")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Get user data to find the avatar URL
            user_response = await client.get(api_url, headers=create_github_headers())
            user_response.raise_for_status()
            user_data = user_response.json()

            avatar_url = user_data.get("avatar_url")
            if not avatar_url:
                message = f"Could not find avatar URL for user '{owner}'."
                await ctx.info(message)
                return None

            # 2. Fetch the image from the avatar URL
            await ctx.info(f"Fetching image from {avatar_url}")
            image_response = await client.get(avatar_url)
            image_response.raise_for_status()
            image_data = image_response.content

            # 3. Return the image object and a success message
            image = Image(data=image_data, format="png")
            await ctx.info(f"Successfully retrieved avatar for '{owner}'.")
            return image

        except httpx.HTTPStatusError as e:
            message = f"GitHub API error: {e.response.status_code} - {e.response.text}"
            await ctx.info(f"Failed to get repository image: {message}")
            return None
        except Exception as e:
            message = f"An unexpected error occurred: {str(e)}"
            await ctx.info(f"Failed to get repository image: {message}")
            return None

@mcp.tool()
async def analyze_repository_activity(owner: str, repo_name: str, ctx: Context) -> dict:
    """
    Analyze repository activity with detailed progress reporting.
    
    This function demonstrates Context capabilities while performing useful analysis.
    """
    await ctx.info("Starting repository activity analysis...")
    total_steps = 5
    
    # Step 1: Get repository info
    await ctx.report_progress(1, total_steps, "Fetching repository information...")
    repo_info = await get_repository_info(owner, repo_name)
    
    # Step 2: Get recent issues
    await ctx.report_progress(2, total_steps, "Analyzing recent issues...")
    issues = await list_repository_issues(owner, repo_name, ctx)
    
    # Step 3: Analyze issue patterns
    await ctx.report_progress(3, total_steps, "Detecting patterns in issues...")
    # Simulate complex analysis with delay
    await anyio.sleep(1)
    
    # Step 4: Calculate metrics
    await ctx.report_progress(4, total_steps, "Calculating activity metrics...")
    metrics = {
        "total_issues": len(issues) if isinstance(issues, list) else 0,
        "avg_comments": sum(issue.get('comments', 0) for issue in issues if isinstance(issue, dict)) / len(issues) if issues else 0,
        "active_contributors": len(set(issue.get('user') for issue in issues if isinstance(issue, dict)))
    }
    
    # Step 5: Generate report
    await ctx.report_progress(5, total_steps, "Generating final report...")
    
    result = {
        "repository": f"{owner}/{repo_name}",
        "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": metrics,
        "summary": f"Repository has {metrics['total_issues']} recent issues with {metrics['active_contributors']} contributors",
        "repo_info": repo_info,
    }
    
    await ctx.info("Repository activity analysis completed successfully!")
    return result


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
