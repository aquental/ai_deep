import uuid
from core.agent import Agent
from core.models.state import State

agent = Agent()

state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "What is 2 + 3?"
        }
    ]
)

# Seed a mock tool call to verify deferred execution
state.pending_tool_calls = [
    {
        "name": "sum_numbers",
        "arguments": {"a": 2, "b": 3},
        "call_id": "call_1",
        "type": "function_call"
    }
]

# Run one step — the seeded call should be executed first, then the LLM queues new calls
state = agent._next_step(state)

# Verify the deferred execution worked
print(f"Steps: {state.steps}")
print(f"Status: {state.status}")

# The executed tool call and its output should appear in context
for entry in state.context:
    if entry.get("type") in ("function_call", "function_call_output"):
        print(entry)

# The LLM should have queued new pending calls for the next step
print(f"New pending tool calls: {len(state.pending_tool_calls)}")
