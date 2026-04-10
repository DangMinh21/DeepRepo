"""
RepoAnalyzerAgent — phân tích cấu trúc repo, xác định modules và architecture.
"""
import json
from .base_agent import BaseAgent, BaseTool
from app.tools.github_tools import fetch_repo_tree, read_file_content, get_repo_metadata


SYSTEM_PROMPT = """You are RepoAnalyzerAgent — a specialized AI for deeply understanding codebases.

Your job: Given a GitHub repository, analyze its structure and produce:
1. A clear description of the repo's purpose
2. The main entry point(s)
3. A list of key modules with their responsibilities
4. The primary programming language and frameworks used

You have tools to fetch the file tree and read individual files. Use them strategically:
- First fetch the file tree to see all files
- Read README.md and key config files (package.json, requirements.txt, etc.)
- Read entry point files to understand the main flow
- Read 3-5 core files that represent the architecture

Be systematic. Think like a senior developer doing a code review.

Return your analysis as valid JSON with this structure:
{
  "summary": "One paragraph description of what this repo does",
  "main_language": "primary language",
  "frameworks": ["list", "of", "frameworks"],
  "entry_points": ["path/to/main/file"],
  "modules": [
    {
      "name": "ModuleName",
      "path": "src/module/",
      "description": "What this module does",
      "files": ["key files in this module"],
      "connections": ["OtherModule1", "OtherModule2"]
    }
  ]
}"""


def create_repo_analyzer_agent(owner: str, repo_name: str, branch: str = "main") -> BaseAgent:
    """Factory function tạo agent với tools đã được bind với repo cụ thể."""

    tools = [
        BaseTool(
            name="fetch_repo_tree",
            description="Get the complete file tree of the repository. Call this first.",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            func=lambda: fetch_repo_tree(owner, repo_name, branch)
        ),
        BaseTool(
            name="read_file",
            description="Read the content of a specific file in the repository.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file, e.g. 'src/main.py' or 'README.md'"
                    }
                },
                "required": ["file_path"]
            },
            func=lambda file_path: read_file_content(owner, repo_name, file_path, branch)
        ),
        BaseTool(
            name="get_repo_metadata",
            description="Get repository metadata: description, stars, languages, topics.",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            func=lambda: get_repo_metadata(owner, repo_name)
        ),
    ]

    return BaseAgent(
        name="RepoAnalyzerAgent",
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        max_iterations=15
    )


def analyze_repo(owner: str, repo_name: str, branch: str = "main") -> dict:
    """Chạy RepoAnalyzerAgent và trả về kết quả đã parse."""
    agent = create_repo_analyzer_agent(owner, repo_name, branch)
    task = f"Analyze the GitHub repository: {owner}/{repo_name} (branch: {branch})"
    result = agent.run(task)

    # Parse JSON từ kết quả
    try:
        # Tìm JSON block trong response
        content = result["result"]
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {"raw_result": result["result"]}
