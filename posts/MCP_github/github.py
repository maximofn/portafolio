import os
from dotenv import load_dotenv

# Load the GitHub token from the .env file
load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Check if the GitHub token is configured
if not GITHUB_TOKEN:
    print("WARNING: The GITHUB_TOKEN environment variable is not configured.")
    print("Requests to the GitHub API may fail due to rate limits.")
    print("Create a .env file in this directory with GITHUB_TOKEN='your_token_here'")
    raise ValueError("GITHUB_TOKEN is not configured")

# Helper function to create headers for GitHub API requests
def create_github_headers():
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    # GitHub recommends including a User-Agent
    headers["User-Agent"] = "MCP_GitHub_Server_Example"
    headers["Accept"] = "application/vnd.github.v3+json" # Good practice
    return headers