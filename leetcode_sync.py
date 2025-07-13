import os
import requests
import time
import subprocess
from datetime import datetime

# === CONFIG ===
USERNAME = "ritik7425singh"
SAVE_DIR = "LeetCodeSolutions"
LIMIT = 1000

HEADERS = {
    'Content-Type': 'application/json',
    'Origin': 'https://leetcode.com',
    'Referer': f'https://leetcode.com/{USERNAME}/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
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

def fetch_all_code_snippets(slug):
    payload = {
        "query": QUESTION_QUERY,
        "variables": {
            "titleSlug": slug
        }
    }
    try:
        response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload)
        time.sleep(0.5)  # avoid hitting rate limits
        if response.status_code == 200:
            data = response.json()
            return data['data']['question']['codeSnippets']
        else:
            print(f"⚠️ Failed to fetch for {slug}: Status {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error for {slug}: {e}")
        return []

def save_code_file(title, code, lang, timestamp):
    ext = {
        "cpp": "cpp", "java": "java", "python3": "py", "python": "py", "c": "c"
    }.get(lang.lower(), "txt")

    lang_folder = os.path.join(SAVE_DIR, lang.lower())
    if not os.path.exists(lang_folder):
        os.makedirs(lang_folder)

    filename = sanitize_filename(title) + f".{ext}"
    filepath = os.path.join(lang_folder, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"// Synced on {datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(code)

    print(f"✓ Saved: {filename} ({lang})")

def git_commit_and_push():
    print("\n📤 Committing and pushing to GitHub...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Update LeetCode solutions"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Pushed to GitHub.")

def main():
    print(f"📥 Fetching accepted submissions for user: {USERNAME}")
    submissions = fetch_recent_submissions(USERNAME)

    if not submissions:
        print("❌ No submissions found or invalid username.")
        return

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    for sub in submissions:
        snippets = fetch_all_code_snippets(sub['titleSlug'])
        for snippet in snippets:
            save_code_file(sub['title'], snippet['code'], snippet['lang'], sub['timestamp'])

    git_commit_and_push()

if __name__ == "__main__":
    main()

