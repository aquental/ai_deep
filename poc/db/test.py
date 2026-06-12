import uuid
import requests

BASE_URL = "http://localhost:8000"

# 1. Launch an agent
res = requests.post(f"{BASE_URL}/agent/launch",
                    json={"input_prompt": "What is 2 + 2?"})
res.raise_for_status()
launch_data = res.json()
state_id = launch_data["id"]
print(f"Launched agent with ID: {state_id}")

# 2. Retrieve state via the GET endpoint (now reading from SQLite)
print("\nRetrieving state from database...")
res = requests.get(f"{BASE_URL}/agent/state/{state_id}")
res.raise_for_status()
state = res.json()

# 3. Check all expected fields exist
print(
    f"\nState: id={state['id']} status={state['status']} steps={state['steps']}")
