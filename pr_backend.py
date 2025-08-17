import sys
import re
from github import Github, GithubException
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def fetch_pr_details(pr_url, output_path='pr_summary.md'):
    # Robustly parse PR URL
    m = re.match(r'https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
    if not m:
        print(f"ERROR: Invalid GitHub PR URL: {pr_url}")
        return False

    owner, repo_name, pr_number_str = m.groups()
    pr_number = int(pr_number_str)

    # Debug prints for tracing values
    print("DEBUG: parsed owner=", owner)
    print("DEBUG: parsed repo_name=", repo_name)
    print("DEBUG: parsed pr_number=", pr_number)

    if not GITHUB_TOKEN or GITHUB_TOKEN == 'your-github-token-here':
        print("WARNING: GITHUB_TOKEN is not set or is the placeholder. Set GITHUB_TOKEN in your environment for authenticated requests.")

    try:
        g = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()
        print("DEBUG: authenticated Github client created")

        repo_full = f"{owner}/{repo_name}"
        print(f"DEBUG: fetching repo {repo_full}")
        repo = g.get_repo(repo_full)

        print(f"DEBUG: fetching pull request #{pr_number}")
        pr = repo.get_pull(pr_number)

    except GithubException as ge:
        print(f"GITHUB ERROR: {ge.status} - {ge.data if hasattr(ge, 'data') else ge}")
        return False
    except Exception as e:
        print(f"ERROR: Exception while fetching PR data: {e}")
        return False

    files_changed = []
    try:
        for file in pr.get_files():
            files_changed.append(f"- {file.filename} (+{file.additions}/-{file.deletions})")
            files_changed.append(f" {file.patch}")
    except Exception as e:
        print(f"ERROR: failed to enumerate PR files: {e}")

    summary = f"""**Title:** {pr.title}\n**Author:** {pr.user.login}\n**Description:** {pr.body or ''}\n**Total Changes:** {pr.additions + pr.deletions}\n\n### Files Changed\n""" + '\n'.join(files_changed)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path) or '.'
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception:
        pass

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"OK: PR summary written to {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: could not write PR summary to {output_path}: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pr_backend.py <pr_url> [output_path]")
        sys.exit(2)
    pr_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'changes.txt'
    ok = fetch_pr_details(pr_url, output_path)
    sys.exit(0 if ok else 1)
