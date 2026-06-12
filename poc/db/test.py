from server.database import get_db_session, StateModel
import sys
import requests

BASE_URL = "http://localhost:8000"
INPUT_PROMPT = "What is 2 + 2?"

# Launch agent
res = requests.post(f"{BASE_URL}/agent/launch",
                    json={"input_prompt": INPUT_PROMPT})
res.raise_for_status()
state_id = res.json()["id"]
print(f"Launched agent with ID: {state_id}")

# Inspect DB
sys.path.insert(0, "src")

with get_db_session() as session:
    all_states = session.query(StateModel).order_by(StateModel.id).all()
    print(f"\nAll DB states ({len(all_states)}):")
    for s in all_states:
        print(f"- id={s.id} status={s.status} steps={s.steps}")
