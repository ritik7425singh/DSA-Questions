import os
import requests
from datetime import datetime
import subprocess

# === CONFIG ===
USERNAME = "ritik7425singh"
SAVE_DIR = "LeetCodeSolutions"
LIMIT = 1000

HEADERS = {
    'Content-Type': 'application/json',
    'Referer': 'https://leetcode.com',
    'User-Agent': 'Mozilla/5.0'
}

GRAPHQL_URL = 'https://leetcode.com/graphql'

SUBMISSION_QUERY = '''
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
    lang
  }
}
'''

QUESTION_QUERY = '''
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    codeSnippets {
      lang
      code
    }
  }
}
'''

def sanitize_filename(name):
    return ''.join(c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in name)

def fetch_recent_submissions(username):
    payload = {
        "query": SUBMISSION_QUERY,
        "variables": {
            "username": username,
            "limit": LIMIT
        }
    }
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload)
    data = response.json()
    return data['data']['recentAcSubmissionList']

def fetch_code_snippet(slug, lang):
    payload = {
        "query": QUESTION_QUERY,
        "variables": {
            "titleSlug": slug
        }
    }
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload)
    snippets = response.json()['data']['question']['codeSnippets']
    for snippet in snippets:
        if snippet['lang'].lower() == lang.lower():
            return snippet['code']
    return None

def save_code_file(title, code, lang, timestamp):
    ext = {
        "cpp": "cpp", "java": "java", "python3": "py", "c": "c"
    }.get(lang.lower(), "txt")

    filename = sanitize_filename(title) + f".{ext}"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"// Synced on {datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(code)

    print(f"✓ Saved: {filename}")

def git_commit_and_push():
    print("\n📤 Committing and pushing to GitHub...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Update LeetCode solutions"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Pushed to GitHub.")

def main():
    print(f"Fetching accepted submissions for user: {USERNAME}")
    submissions = fetch_recent_submissions(USERNAME)

    if not submissions:
        print("❌ No submissions found or invalid username.")
        return

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    for sub in submissions:
        code = fetch_code_snippet(sub['titleSlug'], sub['lang'])
        if code:
            save_code_file(sub['title'], code, sub['lang'], sub['timestamp'])
        else:
            print(f"✗ Skipped: {sub['title']} (no code for language {sub['lang']})")

    git_commit_and_push()

if __name__ == "__main__":
    main()
