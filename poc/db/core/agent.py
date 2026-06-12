import json
import openai
from pathlib import Path
from typing import List, Any

from core.models.state import State
from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)
from core.utils.context_serializer import serialize_context_to_text


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

        prompt_path = Path(__file__).resolve().parent / \
            "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(
            encoding="utf-8") + extra_instructions

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
        serialized_content = serialize_context_to_text(context)
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=serialized_content,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={
                "effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _next_step(self, state: State):
        state.steps += 1

        for function_call in list(state.pending_tool_calls):
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]
            call_id = function_call["call_id"]

            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),
                "call_id": call_id
            })

            match call_name:
                case "final_answer":
                    state.pending_tool_calls = []
                    state.status = "complete"
                    state.final_answer = call_arguments.get("answer")
                    return state
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

            state.pending_tool_calls.remove(function_call)
            state.context.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            })

        response = self._call_llm(state.context)
        function_calls = [
            item for item in response.output if item.type == "function_call"]

        function_call_dicts = [
            {
                "name": fc.name,
                "arguments": json.loads(fc.arguments),
                "call_id": fc.call_id,
                "type": fc.type
            }
            for fc in function_calls
        ]

        state.pending_tool_calls.extend(function_call_dicts)
        return state

    # Add an optional progress_callback parameter (default None) to this method
    def run(self, state: State, progress_callback=None):
        """Execute agent steps on a given state and persist progress."""
        state = state.model_copy(deep=True)
        state.status = "running"
        state.error = None

        # Check if the agent is resuming (state.steps > 0)
        is_resuming = state.steps > 0
        # Calculate max_steps_allowed: (self.max_steps + state.steps) if resuming, else self.max_steps
        max_steps_allowed = (
            self.max_steps + state.steps) if is_resuming else self.max_steps

        try:
            # Update the loop condition below to use max_steps_allowed instead of self.max_steps
            while state.status == "running" and state.steps < max_steps_allowed:
                state = self._next_step(state)
                # If progress_callback was provided, call it with the current state
                if progress_callback:
                    progress_callback(state)  # Save state after each step

            # Update the condition below to use max_steps_allowed instead of self.max_steps
            if state.status == "running" and state.steps >= max_steps_allowed:
                state.status = "max_steps_reached"

            return state
        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            # Clear pending_tool_calls to an empty list
            state.pending_tool_calls = []
            # If progress_callback was provided, call it with the failed state
            if progress_callback:
                progress_callback(state)  # Save the failed state as well
            return state
