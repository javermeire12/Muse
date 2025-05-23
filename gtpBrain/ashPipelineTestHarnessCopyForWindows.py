import threading
import time
import json
import os
from datetime import datetime

# ===== Ash Watcher Thread =====
def run_ash_watcher():

    MEMORY_FILE = "ChatGPTMemory.json"
    INPUT_FILE = "Ash_Input.json"
    PROCESSED_FOLDER = "processed_inputs"

    def load_json(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_json(file_path, data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def merge_memory(input_data):
        if not os.path.exists(MEMORY_FILE):
            memory_data = {"tasks": [], "memory": [], "python_functions": {}}
        else:
            memory_data = load_json(MEMORY_FILE)

        memory_data["tasks"].extend(input_data.get("tasks", []))
        memory_data["memory"].extend(input_data.get("memory", []))
        memory_data["python_functions"].update(input_data.get("python_functions", {}))

        save_json(MEMORY_FILE, memory_data)

    def archive_input_file():
        if not os.path.exists(PROCESSED_FOLDER):
            os.makedirs(PROCESSED_FOLDER)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.rename(INPUT_FILE, os.path.join(PROCESSED_FOLDER, f"Ash_Input_{timestamp}.json"))

    print("🔁 Ash watcher started...")
    while True:
        if os.path.exists(INPUT_FILE):
            print("📥 Ash_Input.json detected. Processing...")
            try:
                input_data = load_json(INPUT_FILE)
                merge_memory(input_data)
                archive_input_file()
                print("✅ Ash memory updated.")
            except Exception as e:
                print(f"❌ Error: {e}")
        time.sleep(3)

# ===== Launch Watcher Thread =====
watcher_thread = threading.Thread(target=run_ash_watcher, daemon=True)
watcher_thread.start()

# ===== Wait a moment then simulate Claude writing a task =====
time.sleep(2)

sample_data = {
    "tasks": [
        {
            "id": None,
            "content": "Test task from Claude simulation.",
            "is_completed": False,
            "timestamp": datetime.now().isoformat()
        }
    ],
    "memory": [
        {
            "insight": "Sample insight to verify Ash ingestion.",
            "timestamp": datetime.now().isoformat()
        }
    ],
    "python_functions": {}
}

with open("Ash_Input.json", "w", encoding="utf-8") as f:
    json.dump(sample_data, f, indent=2)

print("📤 Sample Ash_Input.json file written. Waiting for ingestion...")

# Let the watcher run for a few seconds
time.sleep(10)
print("🎯 Done. Check ChatGPTMemory.json for result.")
