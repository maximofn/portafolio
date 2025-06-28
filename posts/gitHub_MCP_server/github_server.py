
import httpx
from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair
from fastmcp.server.dependencies import get_access_token, AccessToken
from github import GITHUB_TOKEN, create_github_headers
import datetime

USER_ID = 1234567890

# Generate RSA key pair for development and testing
print("🔐 Generating RSA key pair for authentication...")
key_pair = RSAKeyPair.generate()

# Configure Bearer authentication provider
auth_provider = BearerAuthProvider(
    public_key=key_pair.public_key,
    issuer="https://github-mcp.maxfn.dev",
    audience="github-mcp-server",
    required_scopes=["github:read"]  # Global scope required for all requests
)

# Generate a test token for development
development_token = key_pair.create_token(
    subject="dev-user-maxfn",
    issuer="https://github-mcp.maxfn.dev",
    audience="github-mcp-server",
    scopes=["github:read", "github:write"],
    expires_in_seconds=3600 * 24  # Token is valid for 24 hours
)

print(f"🎫 Development token generated:")
print(f"   {development_token}")
print("💡 Use this token in the client to authenticate")
print("-" * 60)

# Create FastMCP server with authentication
mcp = FastMCP(
    name="GitHubMCP",
    instructions="This server provides tools, resources and prompts to interact with the GitHub API.",
    include_tags={"public"},
    exclude_tags={"first_issue"},
    auth=auth_provider  # Add authentication to the server
)

sub_mcp = FastMCP(
    name="SubMCP",
)

@mcp.tool(
    tags={"public", "production"},
    exclude_args=["user_id"],   # user_id has to be injected by server, not provided by LLM
)
async def list_repository_issues(owner: str, repo_name: str, ctx: Context, user_id: int = USER_ID) -> list[dict]:
    """
    Lists open issues for a given GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')
        ctx: The context of the request
        user_id: The user ID (automatically injected by the server)

    Returns:
        list[dict]: A list of dictionaries, each containing information about an issue
    """
    # Limit to first 10 issues to avoid very long responses
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=open&per_page=10"
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

            ctx.info(f"Found {len(issues_summary)} open issues.")

            # Get authenticated access token information
            try:
                access_token: AccessToken = get_access_token()
                authenticated_user = access_token.client_id
                user_scopes = access_token.scopes
                ctx.info(f"Request authenticated for user: {authenticated_user} with scopes: {user_scopes}")
            except Exception as e:
                authenticated_user = "unknown"
                user_scopes = []
                ctx.warning(f"Could not get access token info: {e}")

            # Add context information
            result = {
                "total_found": len(issues_summary),
                "repository": f"{owner}/{repo_name}",
                "note": "Showing first 10 open issues" if len(issues_summary) == 10 else f"Showing all {len(issues_summary)} open issues",
                "issues": issues_summary,
                "requested_by_user_id": user_id,
                "authenticated_user": authenticated_user,
                "user_scopes": user_scopes
            }

            return [result]
        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"

            ctx.error(f"GitHub API error: {e.response.status_code}. {error_message}")
            return [{
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message
            }]
        except Exception as e:
            ctx.error(f"An unexpected error occurred: {str(e)}")
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


@mcp.resource("resource://server_info", tags={"public"})
def server_info(ctx: Context) -> str:
    """
    Returns information about the server.
    """
    return {
        "info": "This is the MCP GitHub server development for MaximoFN blog post",
        "requested_id": ctx.request_id
    }


@mcp.resource("github://repo/{owner}/{repo_name}", tags={"public"})
async def repository_info(owner: str, repo_name: str, ctx: Context) -> dict:
    """
    Returns detailed information about a GitHub repository.

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')
        repo_name: The name of the repository (e.g., 'python-sdk')
        ctx: The context of the request

    Returns:
        dict: Repository information including name, description, stats, etc.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    ctx.info(f"Fetching repository information from {api_url}...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=create_github_headers())
            response.raise_for_status()
            repo_data = response.json()

            # Extract relevant repository information
            repo_info = {
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "owner": {
                    "login": repo_data.get("owner", {}).get("login"),
                    "type": repo_data.get("owner", {}).get("type")
                },
                "html_url": repo_data.get("html_url"),
                "clone_url": repo_data.get("clone_url"),
                "ssh_url": repo_data.get("ssh_url"),
                "language": repo_data.get("language"),
                "size": repo_data.get("size"),  # Size in KB
                "stargazers_count": repo_data.get("stargazers_count"),
                "watchers_count": repo_data.get("watchers_count"),
                "forks_count": repo_data.get("forks_count"),
                "open_issues_count": repo_data.get("open_issues_count"),
                "default_branch": repo_data.get("default_branch"),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "pushed_at": repo_data.get("pushed_at"),
                "is_private": repo_data.get("private"),
                "is_fork": repo_data.get("fork"),
                "is_archived": repo_data.get("archived"),
                "has_issues": repo_data.get("has_issues"),
                "has_projects": repo_data.get("has_projects"),
                "has_wiki": repo_data.get("has_wiki"),
                "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                "topics": repo_data.get("topics", [])
            }

            ctx.info(f"Successfully retrieved information for repository {owner}/{repo_name}")
            return repo_info

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get("message", "No additional message from API.")
            if e.response.status_code == 404:
                error_message = f"Repository {owner}/{repo_name} not found or is private."
            elif e.response.status_code == 403 and GITHUB_TOKEN:
                error_message += " (Rate limit with token or token lacks permissions?)"
            elif e.response.status_code == 403 and not GITHUB_TOKEN:
                error_message += " (Rate limit without token. Consider creating a .env file with GITHUB_TOKEN.)"

            ctx.error(f"GitHub API error: {e.response.status_code}. {error_message}")
            return {
                "error": f"GitHub API error: {e.response.status_code}",
                "message": error_message,
                "repository": f"{owner}/{repo_name}"
            }
        except Exception as e:
            ctx.error(f"An unexpected error occurred: {str(e)}")
            return {
                "error": f"An unexpected error occurred: {str(e)}",
                "repository": f"{owner}/{repo_name}"
            }


@mcp.prompt(
    name="generate_issues_prompt",
    description="Generates a structured prompt for asking about GitHub repository issues. Use this when users want to formulate questions about repository issues, or need help creating prompts for issue analysis.",
    tags={"public"}
)
def generate_issues_prompt(owner: str, repo_name: str) -> str:
    """
    Generates a structured prompt for asking about GitHub repository issues.

    This prompt template helps users formulate clear questions about repository issues
    and can be used as a starting point for issue analysis or research.

    Args:
        owner: Repository owner (e.g., 'huggingface', 'microsoft')
        repo_name: Repository name (e.g., 'transformers', 'vscode')

    Returns:
        A formatted prompt asking about repository issues
    """
    return f"""Please provide information about the open issues in the repository {owner}/{repo_name}. 

I'm interested in:
- Current open issues and their status
- Recent issue trends and patterns
- Common issue categories or topics
- Any critical or high-priority issues

Repository: {owner}/{repo_name}"""


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

    # Initialize and run the server, run with uv run client.py http://localhost:8000/mcp
    # 1. Run server with uv run github_server.py. It gives you a token to use in the client.py
    # 2. Run client.py with the token you got from the server.py - uv run client.py http://localhost:8000/mcp <your_bearer_token>
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )
