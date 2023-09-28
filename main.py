from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)

GITHUB_API_URL = "https://api.github.com"
GITHUB_API_TOKEN = "5550123"  # Replace this with your personal token

class GitHubRepository:
    def __init__(self, name, owner, branches):
        self.name = name
        self.owner = owner
        self.branches = branches

@app.route("/repositories", methods=["GET"])
def list_user_repositories():
    username = request.headers.get("Username")
    accept = request.headers.get("Accept")

    try:
        if accept != "application/json":
            return jsonify({"status": 406, "message": "Unsupported Media Type"}), 406

        headers = {"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        github_api_url = f"{GITHUB_API_URL}/users/{username}/repos"
        response = requests.get(github_api_url, headers=headers)

        if response.status_code == 404:
            return jsonify({"status": 404, "message": "User not found"}), 404
        elif response.status_code != 200:
            return jsonify({"status": 500, "message": f"GitHub API error: {response.text}"}), 500

        repositories_data = response.json()
        repositories_info = []
        for repo_data in repositories_data:
            if not repo_data.get("fork", False):
                branches_url = repo_data["branches_url"].replace("{/branch}", "")
                branches_response = requests.get(branches_url, headers=headers)
                if branches_response.status_code == 200:
                    branches_data = branches_response.json()
                    branches_info = [{"name": branch["name"], "last_commit_sha": branch["commit"]["sha"]} for branch in branches_data]
                    repositories_info.append(GitHubRepository(
                        name=repo_data["name"],
                        owner={"login": repo_data["owner"]["login"]},
                        branches=branches_info,
                    ).__dict__)

        return jsonify(repositories_info)

    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)