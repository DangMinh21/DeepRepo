"""
GitHub Tools — dùng bởi các agents để đọc repo.
Mỗi tool là 1 function Python thuần, không phụ thuộc vào AI provider.
Agent sẽ gọi các tool này thông qua tool-calling interface.
"""
import os
import base64
from github import Github, GithubException
from typing import Optional


def _get_github_client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    return Github(token) if token else Github()


def fetch_repo_tree(owner: str, repo_name: str, branch: str = "main") -> dict:
    """
    Lấy toàn bộ file tree của repo (flatten list).
    Returns: {"files": [...], "total": int, "truncated": bool}
    """
    g = _get_github_client()
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        # Thử branch được chỉ định, fallback về default branch
        try:
            tree = repo.get_git_tree(branch, recursive=True)
        except GithubException:
            tree = repo.get_git_tree(repo.default_branch, recursive=True)

        files = []
        for item in tree.tree:
            if item.type == "blob":  # chỉ lấy file, không lấy folder
                files.append({
                    "path": item.path,
                    "size": item.size,
                    "type": "file"
                })

        return {
            "files": files[:500],  # giới hạn 500 files
            "total": len(tree.tree),
            "truncated": tree.truncated
        }
    except GithubException as e:
        return {"error": str(e), "files": [], "total": 0}


def read_file_content(owner: str, repo_name: str, file_path: str, branch: str = "main") -> dict:
    """
    Đọc nội dung 1 file từ repo.
    Returns: {"content": str, "size": int, "encoding": str}
    """
    g = _get_github_client()
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        try:
            file_content = repo.get_contents(file_path, ref=branch)
        except GithubException:
            file_content = repo.get_contents(file_path, ref=repo.default_branch)

        if isinstance(file_content, list):
            return {"error": "Path is a directory, not a file"}

        if file_content.size > 100_000:  # skip file > 100KB
            return {"error": f"File too large ({file_content.size} bytes)", "size": file_content.size}

        content = base64.b64decode(file_content.content).decode("utf-8", errors="replace")
        return {
            "content": content,
            "size": file_content.size,
            "path": file_path
        }
    except GithubException as e:
        return {"error": str(e)}


def get_repo_metadata(owner: str, repo_name: str) -> dict:
    """
    Lấy metadata của repo: ngôn ngữ, description, stars, topics.
    """
    g = _get_github_client()
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        languages = repo.get_languages()
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "default_branch": repo.default_branch,
            "stars": repo.stargazers_count,
            "languages": dict(languages),
            "topics": repo.get_topics(),
            "created_at": repo.created_at.isoformat(),
        }
    except GithubException as e:
        return {"error": str(e)}


def parse_github_url(url: str) -> Optional[dict]:
    """
    Parse GitHub URL thành owner và repo_name.
    Hỗ trợ: https://github.com/owner/repo và github.com/owner/repo
    """
    url = url.strip().rstrip("/")
    # Remove .git suffix
    if url.endswith(".git"):
        url = url[:-4]

    parts = url.replace("https://", "").replace("http://", "").split("/")
    if len(parts) >= 3 and parts[0] == "github.com":
        return {"owner": parts[1], "repo_name": parts[2]}
    return None
