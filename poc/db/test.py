import time
import json
import requests

BASE_URL = "http://localhost:8000"

# 1. Launch an agent
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "What is 2 + 2?"}
)
response.raise_for_status()
state = response.json()
print(f"Launched agent with ID: {state['id']}")
print(f"Initial status: {state['status']}")

# 2. Poll until the agent reaches a terminal status
print("\nPolling for progress...")
while True:
    time.sleep(1)
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    response.raise_for_status()
    current = response.json()

    print(f"Status: {current['status']} | Steps: {current['steps']}")

    if current["status"] in ("complete", "max_steps_reached", "failed"):
        break

# 3. Display the final result
print(f"\nFinal status: {current['status']}")
print(f"Final answer: {current.get('final_answer')}")
print(f"Total steps: {current['steps']}")
