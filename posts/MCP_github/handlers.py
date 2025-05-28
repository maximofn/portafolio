import httpx
from github import GITHUB_TOKEN, create_github_headers

def register_handlers(mcp):
    # List available resources
    @mcp.resource("hello://{nombre}")
    def greeting(nombre: str) -> str:
        """
        Returns a personalized greeting. The LLM can use this tool to greet the user.
        For example, if the user's name is "Max", the LLM can invoke this tool
        and get "¡Hola, Max!".

        Args:
            nombre (str): The name of the person to greet.

        Returns:
            str: A personalized greeting.
        """
        return f"Hello, {nombre}!"
    
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