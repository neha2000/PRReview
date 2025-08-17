"""
GitHub PR Review module using PyGithub and VS Code Language Model
"""

from github import Github
import os
import sys
from typing import Optional

try:
    from vscode import commands, window
    import vscode
except ImportError:
    print("This script must be run as a VS Code extension")
    sys.exit(1)
class PRReviewer:
    def __init__(self, github_token):
        self.github = Github(github_token)

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

    async def review_pr(self, pr_data):
        """
        Review PR using VS Code's Copilot Chat Extension
        """
        try:
            if not pr_data:
                return "Error: No PR data available to review"

            # Prepare the review request prompt
            prompt = f"""Review this pull request and provide detailed feedback:

Title: {pr_data['title']}
Description: {pr_data['body']}
Author: {pr_data['user']}
Total Changes: {pr_data['total_changes']} lines

Files Changed:
{self._format_files_summary(pr_data['files_changed'])}

Please analyze:
1. Code quality and style
2. Potential bugs or issues
3. Security concerns
4. Performance implications
5. Best practices
"""
            # Create temporary markdown file with the PR details
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
                f.write(prompt)
                temp_file = f.name
            
            # Open the file in VS Code and then trigger Copilot Chat
            os.system(f'code -r "{temp_file}"')
            print("\nPR details have been opened in VS Code.")
            print("Please use GitHub Copilot Chat to review the PR:")
            print("1. Press Ctrl+I (or Cmd+I on Mac) to open Copilot Chat")
            print("2. Ask for a review of the PR")
            print("3. Copy the generated review when ready")
            
            return "PR review process initiated in VS Code with Copilot Chat"
            
        except Exception as e:
            print(f"Error during review: {e}")
            return f"Error generating review: {str(e)}"

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

async def main():
    try:
        # Get GitHub token from environment variable
        github_token = "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"  # os.getenv("GITHUB_TOKEN")

        if not github_token:
            print("Error: Please set GITHUB_TOKEN environment variable")
            return

        # Initialize reviewer
        reviewer = PRReviewer(github_token)

        # Example PR URL
        pr_url = "https://github.com/neha2000/hashicat-aws/pull/1"

        # Get PR details
        print("Fetching PR details...")
        pr_data = reviewer.get_pr_details(pr_url)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return

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
        review = await reviewer.review_pr(pr_data)  # Add await here
        print("\nReview Feedback:")
        print(review)
    else:
        print("Failed to fetch PR details")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
