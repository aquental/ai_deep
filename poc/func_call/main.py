import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

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
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        }
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
    }
]

system_prompt = """
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Initialize messages with system prompt and user request
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Compute 15 + 27 and also compute 8 * 6"}
]

# First API call using Chat Completions (DeepSeek compatible)
response = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=messages,
    tools=tool_schemas,
    tool_choice="auto",
)

# Process the first response: execute function calls and add results to messages
msg = response.choices[0].message
messages.append(msg.model_dump())

for tool_call in msg.tool_calls:
    args = json.loads(tool_call.function.arguments)

    match tool_call.function.name:
        case "add":
            result = add(**args)
        case "multiply":
            result = multiply(**args)
        case _:
            result = f"Error: Tool {tool_call.function.name} not implemented"

    print(f"Executed {tool_call.function.name}({args}) = {result}")

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({"result": result})
    })

# Make a second API call with the updated conversation
response2 = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=messages,
    tools=tool_schemas,
    tool_choice="auto",
)

# Process the second response: the model should either return the final answer
# directly as text or call the final_answer tool
msg2 = response2.choices[0].message

if msg2.content:
    print("Final Answer:", msg2.content)
elif msg2.tool_calls:
    for tc in msg2.tool_calls:
        if tc.function.name == "final_answer":
            args = json.loads(tc.function.arguments)
            print("Final Answer:", args.get("answer"))
