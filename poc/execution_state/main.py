import uuid
import json
from core.models.state import State

# TODO: Create a State instance with:
# - id set to a generated UUID string (use str(uuid.uuid4()))
# - context set to a list with one user message dict (role="user", content with a simple request)
# - Leave steps and status unset to exercise their defaults
initial_state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
        }
    ],
    status="running"
)

# TODO: Print state.model_dump() to verify the defaults:
# - steps should be 0
# - status should be "running"
# - pending_tool_calls should be an empty list
# - error and final_answer should be None
print(json.dumps(initial_state.model_dump(), indent=2))
