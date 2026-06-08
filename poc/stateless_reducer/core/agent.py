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

    This exercise focuses on implementing the run method to orchestrate
    the full reducer loop until completion or max_steps is reached.
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
        Execute one step of the agent loop:
        1. Call the LLM
        2. Extract function calls
        3. Execute tools
        4. Update context

        Returns: (updated_context, status, final_answer)
        """
        response = self._call_llm(context)
        function_calls = [
            item for item in response.output if item.type == "function_call"]

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
                    output = json.dumps(
                        {"result": f"Error: Tool {call_name} not found"})

            # Record the tool output in context
            context.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": output
            })

        # All tools executed, continue the loop
        return context, "running", None

    def run(self, context: List[Any]):
        """
        Run the agent loop until completion or max_steps.

        This is the main orchestration method that implements the reducer pattern:
        context in, context out. It repeatedly calls _next_step until the agent
        completes or hits the safety boundary.

        Returns: (final_context, status, final_answer)
            - final_context: The complete conversation history
            - status: "complete" if finished, "max_steps_reached" if hit limit
            - final_answer: The final answer string if complete, None otherwise
        """
        step = 0
        status = "running"
        final_answer = None

        # Keep running until we complete or hit the step limit
        while status == "running" and step < self.max_steps:
            step += 1
            # Each step returns updated context, status, and potentially an answer
            context, status, final_answer = self._next_step(context)

        # If we hit the step limit without completing, update status
        if status == "running":
            status = "max_steps_reached"

        # Return the final state
        return context, status, final_answer
