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

        # Phase 1: Execute pending tool calls from the PREVIOUS step (before calling LLM)
        # Use snapshot for safe iteration while potentially modifying the list
        for call in list(state.pending_tool_calls):
            call_name = call.get("name")
            call_arguments = call.get("arguments", {})  # dict (parsed)
            call_id = call.get("call_id")

            # Append function_call entry to context; serialize arguments to JSON string
            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),
                "call_id": call_id
            })

            if call_name == "final_answer":
                # Special handling for final_answer: clear pending, complete, store answer, return immediately
                state.pending_tool_calls = []
                state.status = "complete"
                state.final_answer = call_arguments.get("answer")
                return state

            # Otherwise, execute the matching math tool in try/except
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

            # Remove the processed call from pending_tool_calls (by call_id for safety)
            state.pending_tool_calls = [
                c for c in state.pending_tool_calls if c.get("call_id") != call_id
            ]

            # Append the function_call_output entry to context
            state.context.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            })

        # Phase 2: Query the LLM and queue new calls (do NOT execute them here)
        response = self._call_llm(state.context)
        function_calls = [
            item for item in response.output if item.type == "function_call"]

        # Convert each function_call into a dict and extend pending_tool_calls for deferred execution
        new_calls = []
        for fc in function_calls:
            call_name = fc.name
            call_arguments = json.loads(fc.arguments)  # parse to dict
            new_calls.append({
                "name": call_name,
                "arguments": call_arguments,
                "call_id": fc.call_id,
                "type": getattr(fc, "type", "function_call")
            })

        state.pending_tool_calls.extend(new_calls)

        return state

    # No changes needed — run already works with the State object
    def run(self, state: State):
        state = state.model_copy(deep=True)
        state.status = "running"
        state.error = None

        try:
            while state.status == "running" and state.steps < self.max_steps:
                state = self._next_step(state)
        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            return state

        if state.status == "running":
            state.status = "max_steps_reached"

        return state
