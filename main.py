"""
main.py - Entry point for the AI PR Review Agent using GPT-4 model
"""

from openai import OpenAI

def ingest_pr_data(pr_url):
    """Ingest PR data from GitHub URL."""
    import requests
    import re
    import os
    try:
        # Extract owner, repo, and PR number from URL
        match = re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
        if not match:
            raise ValueError("Invalid GitHub PR URL format")
        
        owner, repo, pr_number = match.groups()
        
        # Use GitHub API with authentication
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token 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'# {os.getenv("GITHUB_TOKEN")}'
        }
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        print(f"Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
        
        pr_data = response.json()
        print(f"Successfully fetched PR data for {owner}/{repo}#{pr_number}")
        return pr_data
    except Exception as e:
        print(f"Error ingesting PR data: {e}")
        return {}

def review_pr(pr_data):
    """Review PR data using GPT model."""
    try:
        client = OpenAI(
            api_key="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"
        )
        print("API Key set successfully")
        # Prepare the prompt with PR data
        prompt = f"""Review this pull request and provide feedback:
        {pr_data}
        Focus on code quality, potential bugs, and best practices."""
        
        # Get review feedback using GPT-3.5 (most cost-effective)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # This is the most affordable model
            max_tokens=500,  # Reduced tokens to minimize cost
            temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        print(f"Error during review: {error_message}")
        if "insufficient_quota" in error_message:
            return "Error: OpenAI API quota exceeded. Please check your account balance or upgrade your plan."
        return f"Error processing review: {error_message}"

def main():
    pr_path = "https://github.com/neha2000/hashicat-aws/pull/1/files"  # Update with actual PR data path
    pr_data = ingest_pr_data(pr_path)
    feedback = review_pr(pr_data)
    print("PR Review Feedback:", feedback)

if __name__ == "__main__":
    main()
