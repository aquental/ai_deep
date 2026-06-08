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
    """
    A stateless reducer agent that processes context step-by-step.

    This exercise focuses on implementing tool execution with error handling
    using match/case to route function calls to their implementations.
    """

    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        """
        Initialize the Agent with configuration parameters and load tool schemas.

        Args:
            model: The model to use for generation (default: "gpt-5")
            reasoning_effort: The reasoning effort level for gpt-5 (default: "low")
            extra_instructions: Additional instructions to append to the system prompt
            max_steps: Maximum number of steps the agent can take (default: 10)
        """
        # Store model configuration
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps

        # Build the system prompt by combining base prompt with extra instructions
        self.system_prompt = (
            "You are an autonomous agent that can take multiple tool-calling steps. "
            "If your work is done, call the final_answer tool. "
            "ALWAYS prefer calling tools to compute, fetch, or transform information "
            "rather than fabricating results."
        ) + extra_instructions

        # Load tool schemas from JSON files
        # Using Path makes this portable across different environments
        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"

        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)

        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        # Combine all schemas into a single list
        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]

    def _call_llm(self, context: List[Any]):
        """
        Call the LLM with the current context.
        Returns the model's response, which will include tool calls.

        Args:
            context: The full conversation history

        Returns:
            The model's response object
        """
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
        """
        Execute one step of the agent loop - the "reducer" transformation:
        1. Call the LLM to get the next action (function call)
        2. Parse and record the function call in context
        3. Execute the tool and capture its output
        4. Append structured output to context

        This implements the reducer pattern: parse action → execute → append result.

        Returns: (updated_context, status, final_answer)
            - updated_context: The context list with new function calls and outputs
            - status: "complete" if final_answer was called, "running" otherwise
            - final_answer: The answer string if complete, None otherwise
        """
        # Get the model's response
        response = self._call_llm(context)

        # Extract all function calls from the response
        function_calls = [
            item for item in response.output if item.type == "function_call"]

        # Process each function call
        for fc in function_calls:
            call_name = fc.name
            call_arguments = json.loads(fc.arguments)

            # Record the function call in context
            context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })

            # Check if this is the final answer
            if call_name == "final_answer":
                # Stop the loop and return the answer
                return context, "complete", call_arguments.get("answer")

            # Execute the tool based on its name
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
                    # Unknown tool name
                    output = json.dumps(
                        {"result": f"Error: Tool {call_name} not found"})

            # Record the tool output in context, linked to the original call
            context.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": output
            })

        # All tools executed, continue the loop
        return context, "running", None
