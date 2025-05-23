import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_FILE = "memory.json"

# Load memory
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    except json.JSONDecodeError:
        memory = []
else:
    memory = []

# Save a new memory entry
def log_entry(entry_text):
    memory.append({"role": "user", "content": entry_text})
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Use OpenAI API to summarize memory
def summarize_memory():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the user's memory log into a short list of key ideas."},
            *memory
        ]
    )
    return response.choices[0].message.content

# Run the logging/summarizing loop
if __name__ == "__main__":
    log_entry(input("What do you want to remember? "))
    print("Summarizing memory...")
    summary = summarize_memory()
    print("\nSUMMARY:\n", summary)
