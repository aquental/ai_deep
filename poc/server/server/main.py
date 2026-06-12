import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent

agent = Agent()
states: Dict[str, State] = {}

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


def _run_agent_in_background(state_id: str):
    """Executa o agent em background."""
    if state_id not in states:
        return  # segurança extra

    state = states[state_id]
    try:
        # assumindo que retorna o novo estado
        updated_state = agent.run(state)
        states[state_id] = updated_state
    except Exception as e:                    # boa prática
        # você pode marcar como failed
        state.status = "failed"
        state.error = str(e)
        states[state_id] = state
        print(f"Agent failed for {state_id}: {e}")


@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[{"role": "user", "content": payload.input_prompt}],
        status="running",
        steps=0
    )

    states[initial_state.id] = initial_state
    background_tasks.add_task(_run_agent_in_background, initial_state.id)

    return initial_state


@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    if state_id not in states:
        raise HTTPException(status_code=404, detail="State not found")
    return states[state_id]
