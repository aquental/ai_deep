import json
import os

from dotenv import load_dotenv
load_dotenv()

import openai

# Configure OpenAI client for DeepSeek API
openai_client = openai.OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

# Define the functions we want to make available to the model


def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


# Define tool schemas including a special final_answer tool
tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers together",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"}
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers together",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"}
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        }
    }
]

system_prompt = """
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Initialize context with the user's message
context = [
    {
        "role": "user",
        "content": "What is 15 + 27? Then multiply the result by 3."
    }
]

# Set up loop control variables
max_steps = 5
step = 0
done = False
final_answer = None

# Main agent loop: continue until done or max steps reached
while not done and step < max_steps:
    step += 1
    print(f"\n--- Step {step} ---")

    # Call the LLM with current context (Chat Completions API)
    response = openai_client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[{"role": "system", "content": system_prompt}] + context,
        tools=tool_schemas,
        tool_choice="auto",
    )

    # Get the assistant message
    assistant_message = response.choices[0].message

    # If the model responds with text (no tool calls), add it to context
    if assistant_message.content:
        context.append({
            "role": "assistant",
            "content": assistant_message.content
        })

    # Process tool calls
    if assistant_message.tool_calls:
        # Record the assistant message with tool calls in context
        context.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        for tc in assistant_message.tool_calls:
            function_name = tc.function.name
            args = json.loads(tc.function.arguments)

            print(f"Calling function: {function_name}({args})")

            # Execute the requested tool safely
            try:
                if function_name == "final_answer":
                    result = args.get("answer")
                    final_answer = result
                    output = json.dumps({"status": "reported"})
                    done = True
                    print(f"Final answer received: {result}")

                elif function_name == "add":
                    result = add(**args)
                    output = json.dumps({"result": result})
                    print(f"add result: {result}")

                elif function_name == "multiply":
                    result = multiply(**args)
                    output = json.dumps({"result": result})
                    print(f"multiply result: {result}")

                else:
                    result = f"Tool {function_name} not found"
                    output = json.dumps({"error": result})
                    print(result)

            except Exception as e:
                result = f"Error: {e}"
                output = json.dumps({"error": str(e)})
                print(result)

            # Complete the feedback loop: append tool output to context
            context.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": output
            })

            # Exit gracefully if final_answer was called
            if done:
                break
