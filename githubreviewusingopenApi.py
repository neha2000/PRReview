"""
GitHub PR Review module using PyGithub and OpenAI
"""

from github import Github
from openai import OpenAI
import os

class PRReviewer:
    def __init__(self, github_token, openai_api_key):
        self.github = Github(github_token)
        self.openai_client = OpenAI(api_key=openai_api_key)

    def get_pr_details(self, pr_url):
        """
        Extract PR details using PyGithub
        """
        try:
            # Parse PR URL to get owner, repo, and PR number
            # Example URL: https://github.com/owner/repo/pull/number
            parts = pr_url.split('/')
            owner = parts[3]
            repo_name = parts[4]
            pr_number = int(parts[6])
            
            print(f"\nParsed PR URL components:")
            print(f"Owner: {owner}")
            print(f"Repository: {repo_name}")
            print(f"PR Number: {pr_number}")

            # Get repository and pull request
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            # Get PR files and changes
            files_changed = []
            for file in pr.get_files():
                files_changed.append({
                    'filename': file.filename,
                    'status': file.status,
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'changes': file.changes,
                    'patch': file.patch
                })

            pr_data = {
                'title': pr.title,
                'body': pr.body,
                'user': pr.user.login,
                'state': pr.state,
                'created_at': pr.created_at.isoformat(),
                'updated_at': pr.updated_at.isoformat(),
                'files_changed': files_changed,
                'total_changes': pr.additions + pr.deletions
            }

            return pr_data

        except Exception as e:
            print(f"Error fetching PR details: {e}")
            return None

    def review_pr(self, pr_data):
        """
        Review PR using OpenAI's GPT model
        """
        try:
            if not pr_data:
                return "Error: No PR data available to review"

            # Prepare a detailed prompt for the AI
            prompt = f"""Please review this pull request and provide detailed feedback:

Title: {pr_data['title']}
Description: {pr_data['body']}
Author: {pr_data['user']}
Total Changes: {pr_data['total_changes']} lines

Files Changed:
{self._format_files_summary(pr_data['files_changed'])}

Key points to analyze:
1. Code quality and style
2. Potential bugs or issues
3. Security concerns
4. Performance implications
5. Best practices adherence

Please provide specific recommendations for improvement if needed.
"""

            # Get AI review
            # response = self.openai_client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": "You are an expert code reviewer. Provide clear, constructive feedback."},
            #         {"role": "user", "content": prompt}
            #     ],
            #     max_tokens=500,
            #     temperature=0.7
            # )

            return "abe to fetch data"# response.choices[0].message.content

        except Exception as e:
            print(f"Error during review: {e}")
            return f"Error generating review: {str(e)}"

    def _format_files_summary(self, files):
        """Helper method to format files summary"""
        summary = []
        for file in files:
            summary.append(
                f"File: {file['filename']}\n"
                f"Status: {file['status']}\n"
                f"Changes: +{file['additions']} -{file['deletions']}\n"
                f"Patch:\n{file['patch']}\n"
            )
        return "\n".join(summary)

def main():
    # Get credentials from environment variables
    github_token = "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"#os.getenv("GITHUB_TOKEN")
    openai_api_key = "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"# os.getenv("OPENAI_API_KEY")

    if not github_token or not openai_api_key:
        print("Error: Please set GITHUB_TOKEN and OPENAI_API_KEY environment variables")
        return

    # Initialize reviewer
    reviewer = PRReviewer(github_token, openai_api_key)

    # Example PR URL
    pr_url = "https://github.com/neha2000/hashicat-aws/pull/1"

    # Get PR details
    print("Fetching PR details...")
    pr_data = reviewer.get_pr_details(pr_url)

    if pr_data:
        print("\nPR Details:")
        print(f"Title: {pr_data['title']}")
        print(f"Author: {pr_data['user']}")
        print(f"State: {pr_data['state']}")
        print(f"Created: {pr_data['created_at']}")
        print(f"Updated: {pr_data['updated_at']}")
        print(f"\nTotal Changes: {pr_data['total_changes']} lines")
        
        print("\nFiles Changed:")
        for file in pr_data['files_changed']:
            print(f"\nFilename: {file['filename']}")
            print(f"Status: {file['status']}")
            print(f"Changes: +{file['additions']} -{file['deletions']} ({file['changes']} total)")
            print("Patch:")
            print(file['patch'] if file['patch'] else "No patch available")
            print("-" * 80)  # Separator line

        print("\nGenerating review...")
        review = reviewer.review_pr(pr_data)
        print("\nReview Feedback:")
        print(review)
    else:
        print("Failed to fetch PR details")

if __name__ == "__main__":
    main()
