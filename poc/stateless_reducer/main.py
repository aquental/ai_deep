import json
from core.agent import Agent

# Create an agent instance with default settings
agent = Agent()

# Create a context that will trigger a division by zero error
context = [
    {
        "role": "user",
        "content": "Compute 10 divided by 0"
    }
]

# TODO: Call _next_step to execute one iteration and capture:
#   final_context, status, final_answer
final_context, status, final_answer = agent._next_step(context)
# TODO: Print the status
print(f"Status: {status}")
# TODO: Print the resulting context as pretty JSON (hint: json.dumps(..., indent=2))
print("Result:")
print(json.dumps(final_context, indent=2))
