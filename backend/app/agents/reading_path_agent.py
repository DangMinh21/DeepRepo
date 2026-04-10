"""
ReadingPathAgent — tạo lộ trình học tối ưu cho một repo.
Dựa trên kết quả từ RepoAnalyzerAgent.
"""
import json
from .base_agent import BaseAgent, BaseTool
from app.tools.github_tools import read_file_content


SYSTEM_PROMPT = """You are ReadingPathAgent — a specialized AI that creates optimal learning paths through codebases.

Your job: Given a repo analysis, create a step-by-step reading guide so a student can understand the codebase efficiently.

Rules for a good reading path:
1. Start from entry point(s) — understand the "front door" first
2. Follow the execution flow — trace how data flows through the system
3. Read config/setup files early — they explain the environment
4. Group related files together
5. Leave tests and utilities for last
6. Maximum 15 steps for MVP repos, 25 for larger ones

For each step explain:
- WHY they should read this file now (not just what it does)
- What key concepts to look for
- How it connects to the previous file

Return valid JSON:
{
  "reading_path": [
    {
      "order": 1,
      "file_path": "path/to/file.py",
      "reason": "Start here because this is the entry point that bootstraps the entire app",
      "key_concepts": ["dependency injection", "FastAPI app initialization"],
      "estimated_minutes": 10
    }
  ],
  "total_estimated_hours": 2.5
}"""


def create_reading_path_agent(owner: str, repo_name: str, branch: str = "main") -> BaseAgent:
    tools = [
        BaseTool(
            name="read_file",
            description="Read the content of a specific file to better understand its role.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file"
                    }
                },
                "required": ["file_path"]
            },
            func=lambda file_path: read_file_content(owner, repo_name, file_path, branch)
        ),
    ]

    return BaseAgent(
        name="ReadingPathAgent",
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        max_iterations=12
    )


def generate_reading_path(owner: str, repo_name: str, analysis: dict, branch: str = "main") -> dict:
    """Tạo reading path dựa trên analysis từ RepoAnalyzerAgent."""
    agent = create_reading_path_agent(owner, repo_name, branch)

    task = f"""Create a reading path for {owner}/{repo_name}.

Here is the architecture analysis:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Generate the optimal step-by-step reading guide."""

    result = agent.run(task)

    try:
        content = result["result"]
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {"raw_result": result["result"]}
