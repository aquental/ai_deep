import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

# Create DeepSeek client
client = openai.OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ["DEEPSEEK_BASE_URL"],
)

MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")


# Define the functions we want to make available to the model
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


# Define tool schemas for the model (including final_answer)
tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The final answer for the user.",
                    }
                },
                "required": ["answer"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"},
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"},
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
    },
]

system_prompt = """
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Build messages list (Chat Completions API format)
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Compute 15 + 27"},
]

# First API call: the model will see the user's request and available tools
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tool_schemas,
)

# Process the response: execute any function calls
choice = response.choices[0]

if choice.message.tool_calls:
    for tool_call in choice.message.tool_calls:
        fn = tool_call.function
        args = json.loads(fn.arguments)

        # Dispatch to the correct function
        match fn.name:
            case "add":
                result = add(**args)
            case "multiply":
                result = multiply(**args)
            case _:
                result = f"Error: Unknown tool '{fn.name}'"

        # Print verification line
        print(f"Executed {fn.name} with args {args} -> result: {result}")
elif choice.message.content:
    print(f"Model response (no tool calls): {choice.message.content}")
else:
    print("No tool calls or content in response.")
