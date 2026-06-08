import json
import openai
from pathlib import Path
from typing import List, Any

from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)


class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps

        # Load the system prompt from src/core/prompts/base_system.md using Path
        prompt_path = Path(__file__).resolve().parent / \
            "prompts" / "base_system.md"
        # Read the file with UTF-8 encoding and append extra_instructions
        self.system_prompt = prompt_path.read_text(
            encoding="utf-8") + extra_instructions

        # self.system_prompt = (
        #    "You are an autonomous agent that can take multiple tool-calling steps. "
        #    "If your work is done, call the final_answer tool. "
        #    "ALWAYS prefer calling tools to compute, fetch, or transform information "
        #    "rather than fabricating results."
        # ) + extra_instructions

        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]

    def _call_llm(self, context: List[Any]):
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={
                "effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _next_step(self, context: List[Any]):
        response = self._call_llm(context)
        function_calls = [
            item for item in response.output if item.type == "function_call"]

        for fc in function_calls:
            call_name = fc.name
            call_arguments = json.loads(fc.arguments)

            context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })

            if call_name == "final_answer":
                return context, "complete", call_arguments.get("answer")

            match call_name:
                case "sum_numbers":
                    try:
                        result = sum_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "multiply_numbers":
                    try:
                        result = multiply_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "subtract_numbers":
                    try:
                        result = subtract_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "divide_numbers":
                    try:
                        result = divide_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "power":
                    try:
                        result = power(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "square_root":
                    try:
                        result = square_root(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case _:
                    output = json.dumps(
                        {"result": f"Error: Tool {call_name} not found"})

            context.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": output
            })

        return context, "running", None

    def run(self, context: List[Any]):
        step = 0
        status = "running"
        final_answer = None

        while status == "running" and step < self.max_steps:
            step += 1
            context, status, final_answer = self._next_step(context)

        if status == "running":
            status = "max_steps_reached"

        return context, status, final_answer
