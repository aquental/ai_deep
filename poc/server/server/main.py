import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent

# Create agent
agent = Agent()

# In-memory storage
states: Dict[str, State] = {}

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest):
    # Create initial state with unique ID
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )

    # Store in memory
    states[initial_state.id] = initial_state

    # Run the agent synchronously (executes the full tool-calling loop via _next_step)
    updated_state = agent.run(initial_state)

    # Store the final/updated state back (overwrites the initial one)
    states[initial_state.id] = updated_state

    # Return the updated state (now has status, steps, context with tool calls/outputs, final_answer etc.)
    return updated_state
