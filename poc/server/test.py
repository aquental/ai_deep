import time
import json
import requests

# Set the base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

# Record the start time to measure how long the request takes
start_time = time.time()

# Send a POST request to launch the agent
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
)

# Calculate elapsed time
elapsed = time.time() - start_time

# Parse the response JSON to get the state object
state = response.json()

# Print timing information
print(f"Request took {elapsed:.2f} seconds")
print()

# Print the returned state
print("Returned State:")
print(json.dumps(state, indent=2))
