import uuid
from core.agent import Agent
from core.models.state import State

# Create an agent with max_steps=3 to force an early exit
agent = Agent(max_steps=3)

# Build the initial state
initial_state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
        }
    ]
)

# Call agent.run(initial_state) and store the result in intermediate_state
intermediate_state = agent.run(initial_state)

# Print the intermediate_state using .model_dump_json(indent=2)
print("Intermediate state: ")
print(intermediate_state.model_dump_json(indent=2))

# Create a new Agent instance with max_steps=15
new_agent = Agent(max_steps=15)

# Call new_agent.run() with the intermediate_state and store in final_state
final_state = new_agent.run(intermediate_state)

# Print the final_state using .model_dump_json(indent=2)
print("Final state: ")
print(final_state.model_dump_json(indent=2))
