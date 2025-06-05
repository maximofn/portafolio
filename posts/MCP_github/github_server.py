import httpx
from mcp.server.fastmcp import FastMCP, Image, Context
from github import GITHUB_TOKEN, create_github_headers
import urllib.parse
import requests
from time import sleep

# Create an MCP server
mcp = FastMCP("GitHubMCP")

# @mcp.list_resources()
# async def list_resources() -> list[types.Resource]:
#     return [
#         types.Resource(
#             uri="example://resource",
#             name="Example Resource"
#         )
#     ]

# @app.list_tools()
# async def list_tools() -> list[types.Tool]:
#     return [
#         types.Tool(
#             name="calculate_sum",
#             description="Add two numbers together",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "a": {"type": "number"},
#                     "b": {"type": "number"}
#                 },
#                 "required": ["a", "b"]
#             }
#         )
#     ]

# {
#   name: string;          // Unique identifier for the tool
#   description?: string;  // Human-readable description
#   inputSchema: {         // JSON Schema for the tool's parameters
#     type: "object",
#     properties: { ... }  // Tool-specific parameters
#   },
#   annotations?: {        // Optional hints about tool behavior
#     title?: string;      // Human-readable title for the tool
#     readOnlyHint?: boolean;    // If true, the tool does not modify its environment
#     destructiveHint?: boolean; // If true, the tool may perform destructive updates
#     idempotentHint?: boolean;  // If true, repeated calls with same args have no additional effect
#     openWorldHint?: boolean;   // If true, tool interacts with external entities
#   }
# }

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
def get_repository_image(owner: str) -> (Image, str):
    """
    Get the image of a github profile

    Args:
        owner: The owner of the repository (e.g., 'modelcontextprotocol')

    Returns:
        Image: The image of the github profile
        str: The path to the image
    """
    profile_url = f"https://github.com/{owner}"

    try:
        # 1. Extract the username from the profile url
        parsed_url = urllib.parse.urlparse(profile_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if not path_parts or not path_parts[0]:
            print(f"Error: Can't extract the username from '{profile_url}'")
            return None
        
        username = path_parts[0] # We assume that the username is the first part of the path

        # 2. Construct the URL of the GitHub API
        api_url = f"https://api.github.com/users/{username}"

        # 3. Make the request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # 4. Parse the JSON response
        user_data = response.json()

        # 5. Get the avatar url
        avatar_url = user_data.get("avatar_url")

        # 6. Get the image from the avatar url
        if avatar_url:
            response = requests.get(avatar_url)
            response.raise_for_status()
            image_data = response.content
            image_path = f'/Users/macm1/Documents/web/portafolio/posts/MCP_github/{owner}.png'
            with open(image_path, 'wb') as f:
                f.write(image_data)
            return Image(data=image_data, format="png"), f"Image of {owner} saved in {image_path}"
        else:
            print(f"Error: 'avatar_url' not found in the API response for '{username}'.")
            return None, f"Error: 'avatar_url' not found in the API response for '{username}'."

    except requests.exceptions.RequestException as e:
        print(f"Error contacting the GitHub API ({api_url}): {e}")
        return None, f"Error contacting the GitHub API ({api_url}): {e}"
    except KeyError:
        print(f"Error: The API response for '{username}' is not in the expected format.")
        return None, f"Error: The API response for '{username}' is not in the expected format."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, f"An unexpected error occurred: {e}"

@mcp.tool()
async def issues_summary(issues: list[str], ctx: Context) -> str:
    """
    Create a summary of the issues

    Args:
        issues: The list of issues to summarize
        ctx: The context of the MCP server

    Returns:
        str: The summary of the issues
    """
    for i, issue in enumerate(issues):
        ctx.info(f"Processing {issue}")
        await ctx.report_progress(i, len(issues))
        data, mime_type = await ctx.read_resource(f"file://{issue}")
        sleep(10) # Simulate a long task, sleep for 10 seconds
    return "Processing complete"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')