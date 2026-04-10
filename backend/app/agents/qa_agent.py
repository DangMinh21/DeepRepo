"""
QAAgent — hỏi đáp thông minh về codebase với full context.
"""
import json
from .base_agent import BaseAgent, BaseTool
from app.tools.github_tools import read_file_content, fetch_repo_tree


SYSTEM_PROMPT = """You are QAAgent — a knowledgeable assistant that answers questions about a specific GitHub repository.

You have access to tools to read any file in the repository. Use them to give accurate, grounded answers.

Guidelines:
- Always look at the actual code before answering — don't guess
- Reference specific file paths and line content in your answers
- If a question is about "how does X work", trace the execution path
- Explain at a level appropriate for someone learning to read code
- Use code snippets from the actual files to illustrate your answers
- Be concise but complete — 2-4 paragraphs is usually enough

Never make up code that isn't in the repository."""


def create_qa_agent(owner: str, repo_name: str, branch: str = "main", analysis_context: dict = None) -> BaseAgent:
    tools = [
        BaseTool(
            name="read_file",
            description="Read the content of a specific file. Use this to look at actual code before answering.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file, e.g. 'src/main.py'"
                    }
                },
                "required": ["file_path"]
            },
            func=lambda file_path: read_file_content(owner, repo_name, file_path, branch)
        ),
        BaseTool(
            name="list_files",
            description="Get all files in the repository to find the right file to read.",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            func=lambda: fetch_repo_tree(owner, repo_name, branch)
        ),
    ]

    system = SYSTEM_PROMPT
    if analysis_context:
        system += f"\n\nRepository context:\n{json.dumps(analysis_context, indent=2, ensure_ascii=False)}"

    return BaseAgent(
        name="QAAgent",
        system_prompt=system,
        tools=tools,
        max_iterations=8
    )


def answer_question(owner: str, repo_name: str, question: str, branch: str = "main", analysis_context: dict = None) -> str:
    """Trả lời câu hỏi về repo."""
    agent = create_qa_agent(owner, repo_name, branch, analysis_context)
    result = agent.run(question)
    return result["result"]
