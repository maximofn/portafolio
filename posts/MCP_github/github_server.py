import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP, Image, Context
from mcp.server.fastmcp.prompts import Prompt, PromptManager
from github import GITHUB_TOKEN, create_github_headers
from time import sleep

# Create an MCP server
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
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=open"
    ctx.info(f"Fetching issues from {api_url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            issues_data = response.json()
            
            if not issues_data:
                ctx.info("No open issues found for this repository.")
                return [{"message": "No open issues found for this repository."}]

            issues_summary = []
            for issue in issues_data:
                issues_summary.append({
                    "title": issue.get("title"),
                    "number": issue.get("number"),
                    "user": issue.get("user", {}).get("login"),
                    "url": issue.get("html_url"),
                    "comments": issue.get("comments")
                })
            
            ctx.info(f"Found {len(issues_summary)} open issues.")
            return issues_summary
        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"
            
            ctx.info(f"GitHub API error: {e.response.status_code}. {error_message}")
            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            ctx.info(f"An unexpected error occurred: {str(e)}")
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
    ctx.info(f"Fetching user data for '{owner}' from {api_url}")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Get user data to find the avatar URL
            user_response = await client.get(api_url, headers=create_github_headers())
            user_response.raise_for_status()
            user_data = user_response.json()

            avatar_url = user_data.get("avatar_url")
            if not avatar_url:
                message = f"Could not find avatar URL for user '{owner}'."
                ctx.info(message)
                return None

            # 2. Fetch the image from the avatar URL
            ctx.info(f"Fetching image from {avatar_url}")
            image_response = await client.get(avatar_url)
            image_response.raise_for_status()
            image_data = image_response.content

            # 3. Return the image object and a success message
            image = Image(data=image_data, format="png")
            ctx.info(f"Successfully retrieved avatar for '{owner}'.")
            return image

        except httpx.HTTPStatusError as e:
            message = f"GitHub API error: {e.response.status_code} - {e.response.text}"
            ctx.info(f"Failed to get repository image: {message}")
            return None
        except Exception as e:
            message = f"An unexpected error occurred: {str(e)}"
            ctx.info(f"Failed to get repository image: {message}")
            return None

@mcp.tool()
async def issues_summary(issues: list[dict], ctx: Context) -> str:
    """
    Create a summary of the provided issues using an LLM.

    Args:
        issues: The list of issues (as dictionaries) to summarize.
        ctx: The MCP context, used for sampling and logging.

    Returns:
        str: The summary of the issues.
    """
    if not issues or (len(issues) == 1 and "error" in issues[0]):
        return "No issues provided or an error occurred in a previous step."

    ctx.info(f"Summarizing {len(issues)} issues...")
    
    # We will report progress as we format the issues for the prompt
    issue_details = []
    for i, issue in enumerate(issues):
        detail = f"- Issue #{issue.get('number', 'N/A')}: {issue.get('title', 'No Title')} (by {issue.get('user', 'N/A')})"
        issue_details.append(detail)
        await ctx.report_progress(i + 1, len(issues))

    issue_details_str = '\n'.join(issue_details)
    prompt = f"Please provide a concise summary of the following GitHub issues:\n\n"+issue_details_str+"The summary should highlight any recurring themes, urgent problems, or important discussions."
    
    try:
        ctx.info("Sending prompt to LLM for summarization...")
        # Use ctx.sample_text to request a completion from the client's LLM
        summary = await ctx.sample_text(prompt)
        ctx.info("Successfully received summary from LLM.")
        return summary
    except Exception as e:
        error_message = f"Failed to generate summary using the LLM: {str(e)}"
        ctx.info(error_message)
        return error_message


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')