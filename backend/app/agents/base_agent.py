"""
Base Agent — tất cả agents kế thừa class này.
Pattern: agentic loop với tool-calling.
- Agent nhận task + tools
- Gọi LLM với tools definition
- LLM quyết định gọi tool nào
- Agent thực thi tool, trả kết quả lại cho LLM
- Lặp đến khi LLM trả về final answer
"""
import json
import os
from typing import Any, Callable
import litellm


class BaseTool:
    def __init__(self, name: str, description: str, parameters: dict, func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_litellm_format(self) -> dict:
        """Convert sang format mà LiteLLM/OpenAI hiểu."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)


class BaseAgent:
    """
    Agentic loop cơ bản:
    1. Nhận task
    2. Gọi LLM với danh sách tools
    3. Nếu LLM muốn gọi tool → thực thi → trả kết quả
    4. Lặp lại cho đến khi có final answer
    """

    def __init__(self, name: str, system_prompt: str, tools: list[BaseTool], max_iterations: int = 10):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        self.model = os.getenv("AI_MODEL", "claude-sonnet-4-6")

    def _get_tools_definition(self) -> list[dict]:
        return [tool.to_litellm_format() for tool in self.tools.values()]

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        try:
            result = self.tools[tool_name].execute(**tool_args)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

    def run(self, task: str, context: dict = None) -> dict:
        """
        Chạy agentic loop.
        Returns: {"result": str, "tool_calls_made": int, "iterations": int}
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # Thêm context nếu có
        user_message = task
        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            user_message = f"{task}\n\nContext:\n{context_str}"

        messages.append({"role": "user", "content": user_message})

        tool_calls_made = 0
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            response = litellm.completion(
                model=self.model,
                messages=messages,
                tools=self._get_tools_definition() if self.tools else None,
                tool_choice="auto" if self.tools else None,
            )

            message = response.choices[0].message

            # LLM không gọi tool → đây là final answer
            if not message.tool_calls:
                return {
                    "result": message.content,
                    "tool_calls_made": tool_calls_made,
                    "iterations": iteration
                }

            # LLM muốn gọi tools → thực thi
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_calls_made += 1
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_result = self._execute_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        return {
            "result": "Max iterations reached without final answer.",
            "tool_calls_made": tool_calls_made,
            "iterations": iteration
        }
