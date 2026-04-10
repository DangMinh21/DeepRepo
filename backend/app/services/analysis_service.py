"""
AnalysisService — orchestrate toàn bộ pipeline phân tích repo.
Đây là layer kết nối API → Agents.
"""
import hashlib
import json
import os
from app.tools.github_tools import parse_github_url, get_repo_metadata
from app.agents.repo_analyzer_agent import analyze_repo
from app.agents.reading_path_agent import generate_reading_path
from app.models.repo import AnalysisResult, AnalysisStatus


def get_repo_id(github_url: str) -> str:
    """Tạo unique ID cho repo từ URL."""
    return hashlib.sha256(github_url.lower().strip().encode()).hexdigest()[:16]


# In-memory store cho MVP (thay bằng Redis sau)
_analysis_cache: dict[str, dict] = {}


def get_analysis(repo_id: str) -> dict | None:
    return _analysis_cache.get(repo_id)


def save_analysis(repo_id: str, data: dict):
    _analysis_cache[repo_id] = data


async def run_analysis_pipeline(github_url: str) -> str:
    """
    Chạy toàn bộ pipeline phân tích:
    1. Parse URL
    2. Fetch metadata
    3. RepoAnalyzerAgent
    4. ReadingPathAgent
    5. Lưu kết quả

    Returns: repo_id để frontend poll kết quả
    """
    repo_id = get_repo_id(github_url)

    # Parse URL
    parsed = parse_github_url(github_url)
    if not parsed:
        raise ValueError(f"Invalid GitHub URL: {github_url}")

    owner = parsed["owner"]
    repo_name = parsed["repo_name"]

    # Khởi tạo status pending
    save_analysis(repo_id, {
        "repo_id": repo_id,
        "status": AnalysisStatus.pending,
        "repo_url": github_url,
        "repo_name": f"{owner}/{repo_name}",
        "progress_message": "Initializing analysis..."
    })

    # Chạy pipeline (trong production nên dùng background task / queue)
    try:
        # Step 1: Metadata
        save_analysis(repo_id, {**_analysis_cache[repo_id],
            "status": AnalysisStatus.running,
            "progress_message": "Fetching repository metadata..."
        })
        metadata = get_repo_metadata(owner, repo_name)
        total_files = 0

        # Step 2: RepoAnalyzerAgent
        save_analysis(repo_id, {**_analysis_cache[repo_id],
            "progress_message": "AI is analyzing repository architecture... (this takes 30-60s)"
        })
        analysis = analyze_repo(owner, repo_name)

        # Step 3: ReadingPathAgent
        save_analysis(repo_id, {**_analysis_cache[repo_id],
            "progress_message": "AI is generating your personalized reading path..."
        })
        reading_result = generate_reading_path(owner, repo_name, analysis)

        # Step 4: Save final result
        langs = metadata.get("languages") or {}
        main_language = max(langs, key=langs.get) if langs else None

        modules = analysis.get("modules") or []
        if not isinstance(modules, list):
            modules = []

        reading_path = reading_result.get("reading_path") or []
        if not isinstance(reading_path, list):
            reading_path = []

        save_analysis(repo_id, {
            "repo_id": repo_id,
            "status": AnalysisStatus.completed,
            "repo_url": github_url,
            "repo_name": f"{owner}/{repo_name}",
            "total_files": total_files,
            "main_language": main_language,
            "summary": analysis.get("summary") or "",
            "modules": modules,
            "entry_points": analysis.get("entry_points") or [],
            "reading_path": reading_path,
            "progress_message": "Analysis complete!"
        })

    except Exception as e:
        save_analysis(repo_id, {**_analysis_cache.get(repo_id, {}),
            "status": AnalysisStatus.failed,
            "progress_message": f"Analysis failed: {str(e)}"
        })

    return repo_id
