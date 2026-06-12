import time
import json
import requests

BASE_URL = "http://localhost:8000"

# Launch the agent
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
)
state = response.json()
print(f"Launched agent with ID: {state['id']}")

# Poll until the agent completes
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()

    # Display current progress at every polling step
    print(f"Status: {current_state['status']} | Steps: {current_state['steps']} | Pending tool calls: {current_state['pending_tool_calls']}")

    if current_state['status'] in ["complete", "max_steps_reached", "failed"]:
        print("\nFinal State:")
        print(json.dumps(current_state, indent=2))
        break
    
    time.sleep(1)
