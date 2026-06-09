import json
import requests

# Set the base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

# Send a POST request to launch the agent
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
)

# Parse the response JSON to get the initial state object
state = response.json()

# Print the entire state
print(json.dumps(state, indent=2))
