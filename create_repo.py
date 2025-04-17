from github import Github
from dotenv import load_dotenv
import os

# Load .env credentials
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

# Define repo info
repo_name = "ai-blog-autosite"
description = "AI-generated blog about viral side hustles (auto-built with GPT + Hugo)"

# Authenticate with GitHub
g = Github(token)
user = g.get_user()

# Create repo
repo = user.create_repo(
    name=repo_name,
    description=description,
    private=False,
    auto_init=True
)

print(f"✅ Repo created successfully at: {repo.html_url}")
