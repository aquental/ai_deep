import time
import json
import requests

BASE_URL = "http://localhost:8000"

# Launch a new agent that will ask for a missing value
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Can you figure out the area of a circle for me? Use pi = 3.14."}
)
state = response.json()
print(f"Launched agent with ID: {state['id']}")

# Poll until it's waiting for human input
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()
    print(
        f"Status: {current_state['status']}, Steps: {current_state['steps']}")

    if current_state["status"] == "waiting_human_input":
        print("\nAgent is waiting for input. Question:")
        # Extract the question from context
        for item in reversed(current_state.get("context", [])):
            if isinstance(item, dict) and item.get("name") == "ask_human":
                args = json.loads(item.get("arguments", "{}"))
                print(f"- {args.get('question')}")
                break
        break
    time.sleep(1)

# Verify the lifecycle guard on /agent/resume
print("\nAttempting blind resume (should fail with 400)...")
resume_response = requests.post(
    f"{BASE_URL}/agent/resume", json={"id": state["id"]})
print(f"Resume response code: {resume_response.status_code}")
if resume_response.status_code == 400:
    print("Correct! The API rejected a blind resume while waiting for input.")

# Provide human input correctly
print("\nProviding human input via /agent/provide_input...")
requests.post(
    f"{BASE_URL}/agent/provide_input",
    json={"id": state["id"], "answer": "The radius is 10 inches."}
)

# Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()
    print(
        f"Status: {current_state['status']}, Steps: {current_state['steps']}")

    if current_state["status"] in ["complete", "max_steps_reached", "failed"]:
        print(f"\nFinal answer: {current_state.get('final_answer')}")
        break

    time.sleep(1)
