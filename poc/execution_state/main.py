import uuid
from core.agent import Agent
from core.models.state import State

agent = Agent()

# Replace this plain context list with a State instance.
# Use str(uuid.uuid4()) for the id field.
# Put the user message dictionary inside the context field.
# Leave steps and status unset so their defaults apply.
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

# Change this to state = agent.run(state)
state = agent.run(initial_state)

# Print state.status.
# If state.status is "failed", print state.error.
# Otherwise, if state.final_answer is present, print it.
print(f"Status: {state.status}")
print(f"Final answer: {state.final_answer}")
