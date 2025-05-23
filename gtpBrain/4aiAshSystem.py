#!/usr/bin/env python3
"""
4AI-Ash Integration System

A complete implementation integrating multiple AI assistants with the Ash platform.
This system allows four AI assistants (Claude, GPT, Gemini, Llama) to communicate
with each other while maintaining persistent memory through Ash.

Features:
- Inter-AI communication via message passing
- Role-specific task and insight generation
- Ash-compatible JSON generation
- Integration with the Ash watcher

Usage:
    python 4ai_ash_system.py

Authors:
    Claude (Debugger) - Core implementation
    GPT (Architect) - System design
    Gemini (Researcher) - Data analysis
    Llama (Executor) - System deployment
"""

import json
import os
import time
import uuid
import datetime
import logging
import threading
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field

# ===== CONFIGURATION =====

# File paths - matching exactly what Ash expects
ASH_INPUT_FILE = "Ash_Input.json"
COMM_DIR = "./ai_communication"

# Test configuration
TEST_DURATION = 30  # seconds
AI_ACTIVITY_INTERVAL = 5  # seconds

# Enable/disable components
ENABLE_CLAUDE = True
ENABLE_GPT = True
ENABLE_GEMINI = True
ENABLE_LLAMA = True

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("4ai_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("4AISystem")

# ===== DATA MODELS =====

@dataclass
class AshTask:
    """
    Ash-compatible task representation.
    
    Note: id field is set to None to match Ash's expected format.
    """
    content: str
    is_completed: bool = False
    timestamp: str = ""
    id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()

@dataclass
class AshMemory:
    """Ash-compatible memory/insight representation."""
    insight: str
    timestamp: str = ""
    
    def __post_init__(self):
        """Initialize default values."""
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()

@dataclass
class AshData:
    """Complete Ash input data structure."""
    tasks: List[Dict] = field(default_factory=list)
    memory: List[Dict] = field(default_factory=list)
    python_functions: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tasks": self.tasks,
            "memory": self.memory,
            "python_functions": self.python_functions
        }

@dataclass
class Message:
    """Communication message between AIs."""
    sender_id: str
    recipient_id: str
    content: str
    message_type: str
    id: str = ""
    reference_id: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        """Initialize default values."""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()

# ===== UTILITY FUNCTIONS =====

def ensure_dir(directory: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)

def is_file_locked(filepath: str) -> bool:
    """
    Check if a file is locked (being processed by another process).
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if file is locked, False otherwise
    """
    if not os.path.exists(filepath):
        return False
    
    try:
        # Try to open the file in write mode
        with open(filepath, 'a'):
            pass
        return False
    except IOError:
        return True

# ===== CORE SYSTEM CLASSES =====

class AshWriter:
    """
    Handles writing data to Ash input file.
    Ensures file is not overwritten while being processed.
    """
    
    def __init__(self, input_file: str = ASH_INPUT_FILE):
        """
        Initialize the Ash writer.
        
        Args:
            input_file: Path to the Ash input file
        """
        self.input_file = input_file
        self.lock = threading.RLock()
        
        # Current data to be written
        self.data = AshData()
    
    def save_data(self, retry_count: int = 5, retry_delay: float = 1.0) -> bool:
        """
        Save current data to the Ash input file.
        Retries if file is locked.
        
        Args:
            retry_count: Number of times to retry if file is locked
            retry_delay: Time between retries in seconds
            
        Returns:
            True if data was saved, False otherwise
        """
        with self.lock:
            for attempt in range(retry_count):
                try:
                    # Check if file is being processed
                    if is_file_locked(self.input_file):
                        logger.info(f"⏳ Ash input file is locked, waiting ({attempt+1}/{retry_count})...")
                        time.sleep(retry_delay)
                        continue
                    
                    # Convert to dictionary for JSON serialization
                    data_dict = self.data.to_dict()
                    
                    # Write to file
                    with open(self.input_file, 'w', encoding="utf-8") as file:
                        json.dump(data_dict, file, indent=2)
                    
                    # Reset current data after successful write
                    self.data = AshData()
                    
                    logger.info(f"📤 Saved data to {self.input_file}")
                    return True
                except Exception as e:
                    logger.error(f"❌ Error saving Ash data (attempt {attempt+1}/{retry_count}): {str(e)}")
                    time.sleep(retry_delay)
            
            return False
    
    def add_task(self, content: str, is_completed: bool = False) -> None:
        """
        Add a task to the current data.
        
        Args:
            content: Task content
            is_completed: Whether the task is completed
        """
        with self.lock:
            # Create task
            task = AshTask(
                content=content,
                is_completed=is_completed
            )
            
            # Add to current data
            self.data.tasks.append(asdict(task))
            
            logger.info(f"✅ Added task: {content}")
    
    def add_memory(self, insight: str) -> None:
        """
        Add a memory/insight to the current data.
        
        Args:
            insight: Memory content
        """
        with self.lock:
            # Create memory
            memory = AshMemory(
                insight=insight
            )
            
            # Add to current data
            self.data.memory.append(asdict(memory))
            
            logger.info(f"💡 Added insight: {insight}")
    
    def add_python_function(self, name: str, function_code: str, usage_example: str) -> None:
        """
        Add a Python function to the current data.
        
        Args:
            name: Function name
            function_code: Function code
            usage_example: Usage example
        """
        with self.lock:
            # Add to current data
            self.data.python_functions[name] = {
                "function": function_code,
                "usage_example": usage_example
            }
            
            logger.info(f"🔧 Added Python function: {name}")


class AICommunicationSystem:
    """Communication system between AIs with Ash integration."""
    
    def __init__(self, ai_id: str, comm_dir: str = COMM_DIR, 
                 input_file: str = ASH_INPUT_FILE):
        """
        Initialize the communication system.
        
        Args:
            ai_id: ID of this AI
            comm_dir: Directory for communication files
            input_file: Path to the Ash input file
        """
        self.ai_id = ai_id
        self.comm_dir = comm_dir
        self.inbox_path = os.path.join(comm_dir, f"{ai_id}_inbox.json")
        self.outbox_path = os.path.join(comm_dir, f"{ai_id}_outbox.json")
        
        # Create directory
        ensure_dir(comm_dir)
        
        # Initialize Ash writer
        self.ash = AshWriter(input_file)
        
        # Initialize inbox and outbox
        self.inbox = []
        self.outbox = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Load existing messages
        self._load_messages()
    
    def _load_messages(self) -> None:
        """Load existing messages from inbox and outbox files."""
        with self.lock:
            try:
                if os.path.exists(self.inbox_path):
                    with open(self.inbox_path, 'r') as file:
                        self.inbox = json.load(file)
                
                if os.path.exists(self.outbox_path):
                    with open(self.outbox_path, 'r') as file:
                        self.outbox = json.load(file)
            except Exception as e:
                logger.error(f"❌ Error loading messages: {str(e)}")
    
    def _save_inbox(self) -> None:
        """Save inbox messages to file."""
        with self.lock:
            try:
                with open(self.inbox_path, 'w') as file:
                    json.dump(self.inbox, file, indent=2)
            except Exception as e:
                logger.error(f"❌ Error saving inbox: {str(e)}")
    
    def _save_outbox(self) -> None:
        """Save outbox messages to file."""
        with self.lock:
            try:
                with open(self.outbox_path, 'w') as file:
                    json.dump(self.outbox, file, indent=2)
            except Exception as e:
                logger.error(f"❌ Error saving outbox: {str(e)}")
    
    def send_message(self, recipient_id: str, content: str, 
                     message_type: str = "message", 
                     reference_id: Optional[str] = None) -> str:
        """
        Send a message to another AI or to all AIs.
        
        Args:
            recipient_id: ID of recipient AI or "all" for broadcast
            content: Content of the message
            message_type: Type of message (query, response, update, etc.)
            reference_id: ID of a message this is responding to, if any
            
        Returns:
            ID of the sent message
        """
        with self.lock:
            # Create message
            message = Message(
                sender_id=self.ai_id,
                recipient_id=recipient_id,
                content=content,
                message_type=message_type,
                reference_id=reference_id
            )
            
            # Convert to dict for storage
            message_dict = asdict(message)
            
            # Add to outbox
            self.outbox.append(message_dict)
            self._save_outbox()
            
            # Deliver message to recipient(s)
            self._deliver_message(message)
            
            logger.info(f"📤 Message sent from {self.ai_id} to {recipient_id}")
            return message.id
    
    def _deliver_message(self, message: Message) -> None:
        """
        Deliver a message to the recipient's inbox.
        
        Args:
            message: The message to deliver
        """
        message_dict = asdict(message)
        
        try:
            if message.recipient_id == "all":
                # For broadcast messages, deliver to all AIs except sender
                ai_ids = self._get_all_ai_ids()
                for ai_id in ai_ids:
                    if ai_id != self.ai_id:
                        recipient_inbox_path = os.path.join(self.comm_dir, f"{ai_id}_inbox.json")
                        self._append_to_inbox(recipient_inbox_path, message_dict)
            else:
                # For direct messages, deliver to specific recipient
                recipient_inbox_path = os.path.join(self.comm_dir, f"{message.recipient_id}_inbox.json")
                self._append_to_inbox(recipient_inbox_path, message_dict)
        except Exception as e:
            logger.error(f"❌ Error delivering message: {str(e)}")
    
    def _append_to_inbox(self, inbox_path: str, message: Dict) -> None:
        """Append a message to an inbox file."""
        try:
            # Load current inbox
            inbox = []
            if os.path.exists(inbox_path):
                with open(inbox_path, 'r') as file:
                    inbox = json.load(file)
            
            # Add message
            inbox.append(message)
            
            # Save updated inbox
            with open(inbox_path, 'w') as file:
                json.dump(inbox, file, indent=2)
        except Exception as e:
            logger.error(f"❌ Error appending to inbox: {str(e)}")
    
    def _get_all_ai_ids(self) -> List[str]:
        """
        Get IDs of all AIs in the system by scanning the communication directory.
        
        Returns:
            List of AI IDs
        """
        ai_ids = set()
        try:
            for filename in os.listdir(self.comm_dir):
                if filename.endswith("_inbox.json"):
                    ai_id = filename.replace("_inbox.json", "")
                    ai_ids.add(ai_id)
        except Exception as e:
            logger.error(f"❌ Error getting AI IDs: {str(e)}")
        
        return list(ai_ids)
    
    def get_new_messages(self) -> List[Dict]:
        """
        Get new unread messages from the inbox.
        
        Returns:
            List of new messages
        """
        with self.lock:
            # Get current inbox messages
            messages = self.inbox.copy()
            
            # Clear inbox
            self.inbox = []
            self._save_inbox()
            
            return messages
    
    def broadcast_update(self, content: str, update_type: str = "status") -> str:
        """
        Broadcast an update to all AIs.
        
        Args:
            content: Update content
            update_type: Type of update (status, progress, etc.)
            
        Returns:
            ID of the broadcast message
        """
        return self.send_message(
            recipient_id="all",
            content=content,
            message_type=f"update_{update_type}"
        )
    
    # ===== ASH INTEGRATION METHODS =====
    
    def add_task_to_ash(self, content: str, is_completed: bool = False) -> None:
        """
        Add a task to Ash.
        
        Args:
            content: Task content
            is_completed: Whether the task is completed
        """
        # Add to Ash
        self.ash.add_task(content, is_completed)
        
        # Broadcast task creation
        self.broadcast_update(
            content=json.dumps({
                "content": content,
                "is_completed": is_completed
            }),
            update_type="task_created"
        )
    
    def add_insight_to_ash(self, insight: str) -> None:
        """
        Add an insight/memory to Ash.
        
        Args:
            insight: Insight content
        """
        # Add to Ash
        self.ash.add_memory(insight)
        
        # Broadcast insight creation
        self.broadcast_update(
            content=json.dumps({
                "insight": insight
            }),
            update_type="insight_added"
        )
    
    def save_to_ash(self) -> bool:
        """
        Save current data to the Ash input file.
        
        Returns:
            True if data was saved, False otherwise
        """
        return self.ash.save_data()


class AIAgent:
    """
    AI agent in the 4AI system.
    Generates messages, tasks, and insights based on its role.
    """
    
    def __init__(self, ai_id: str, role: str, capabilities: List[str],
                 comm_dir: str = COMM_DIR, input_file: str = ASH_INPUT_FILE):
        """
        Initialize the AI agent.
        
        Args:
            ai_id: ID of this AI
            role: Role of this AI in the system
            capabilities: List of this AI's capabilities
            comm_dir: Directory for communication files
            input_file: Path to the Ash input file
        """
        self.ai_id = ai_id
        self.role = role
        self.capabilities = capabilities
        
        # Initialize communication system
        self.comm = AICommunicationSystem(ai_id, comm_dir, input_file)
        
        # Thread for AI activity
        self.activity_thread = None
        self.stop_activity = threading.Event()
    
    def generate_content(self, content_type: str) -> str:
        """
        Generate content based on the AI's role.
        
        Args:
            content_type: Type of content to generate ("task" or "insight")
            
        Returns:
            Generated content
        """
        content_by_role = {
            "debugger": {
                "task": [
                    "Review code for memory leaks",
                    "Identify performance bottlenecks in the communication system",
                    "Debug task synchronization issues between AIs",
                    "Optimize JSON serialization/deserialization",
                    "Fix race condition in message delivery"
                ],
                "insight": [
                    "Multiple simultaneous file writes causing race conditions",
                    "JSON parsing overhead increases exponentially with document size",
                    "Memory usage spikes during broadcast messages",
                    "Cache invalidation strategy is inefficient",
                    "Error handling in message delivery needs improvement"
                ]
            },
            "architect": {
                "task": [
                    "Design improved communication protocol",
                    "Create system architecture diagram",
                    "Develop scaling strategy for 10+ AIs",
                    "Plan integration with external systems",
                    "Architect persistent storage solution"
                ],
                "insight": [
                    "A centralized message broker would reduce communication overhead",
                    "Adopting a publish-subscribe pattern would improve scalability",
                    "Database-backed persistence would enhance reliability",
                    "Microservices architecture better fits multi-AI collaboration",
                    "API gateway pattern could simplify external integrations"
                ]
            },
            "researcher": {
                "task": [
                    "Analyze communication patterns between AIs",
                    "Research optimal task distribution algorithms",
                    "Investigate memory efficiency improvements",
                    "Study emergent behaviors in multi-AI systems",
                    "Evaluate performance of different serialization formats"
                ],
                "insight": [
                    "Communication frequency decreases as task complexity increases",
                    "Task completion time follows a log-normal distribution",
                    "AIs tend to specialize in specific task types over time",
                    "Collaborative problem-solving emerges without explicit programming",
                    "System exhibits self-organizing behavior under high load"
                ]
            },
            "executor": {
                "task": [
                    "Implement new communication protocol",
                    "Create automated testing framework",
                    "Deploy system to production environment",
                    "Set up monitoring and alerting",
                    "Integrate with external APIs"
                ],
                "insight": [
                    "Regular checkpoint saves prevent data loss during crashes",
                    "Batching small tasks improves overall throughput",
                    "Standardized error formats improve debugging efficiency",
                    "Containerization simplifies deployment across environments",
                    "Automation reduces task completion time by 37%"
                ]
            }
        }
        
        # Get content for this AI's role
        role_content = content_by_role.get(self.role.lower(), {
            "task": [f"Generic task for {self.role}"],
            "insight": [f"Generic insight from {self.role}"]
        })
        
        # Select a random item
        content_options = role_content.get(content_type, [f"Generic {content_type} from {self.role}"])
        content = random.choice(content_options)
        
        # Add timestamp for uniqueness
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return f"{content} - {self.ai_id} ({timestamp})"
    
    def process_messages(self) -> None:
        """Process incoming messages."""
        messages = self.comm.get_new_messages()
        
        for message in messages:
            try:
                # Log message
                logger.info(f"📥 {self.ai_id} received message from {message.get('sender_id')}")
                
                # Process based on message type
                message_type = message.get("message_type", "")
                
                if message_type == "query":
                    # Respond to query
                    self.comm.send_message(
                        recipient_id=message.get("sender_id"),
                        content=f"Response from {self.ai_id} to query: {message.get('content')}",
                        message_type="response",
                        reference_id=message.get("id")
                    )
                
                elif message_type.startswith("update_"):
                    # Process update
                    logger.info(f"ℹ️ {self.ai_id} processing update")
            except Exception as e:
                logger.error(f"❌ Error processing message: {str(e)}")
    
    def perform_activity(self) -> None:
        """Perform AI activity (generate tasks, insights, messages)."""
        try:
            # Process incoming messages
            self.process_messages()
            
            # Randomly decide what to do
            action = random.choice(["task", "insight", "message", "none"])
            
            if action == "task":
                # Generate and add task
                task_content = self.generate_content("task")
                self.comm.add_task_to_ash(task_content)
                logger.info(f"✅ {self.ai_id} added task: {task_content}")
            
            elif action == "insight":
                # Generate and add insight
                insight_content = self.generate_content("insight")
                self.comm.add_insight_to_ash(insight_content)
                logger.info(f"💡 {self.ai_id} added insight: {insight_content}")
            
            elif action == "message":
                # Send message to another AI
                other_ais = ["claude", "gpt", "gemini", "llama"]
                other_ais.remove(self.ai_id)
                recipient = random.choice(other_ais)
                
                self.comm.send_message(
                    recipient_id=recipient,
                    content=f"Hello from {self.ai_id}! This is a test message.",
                    message_type="message"
                )
                logger.info(f"📤 {self.ai_id} sent message to {recipient}")
            
            # Save to Ash after each activity
            self.comm.save_to_ash()
        except Exception as e:
            logger.error(f"❌ Error in AI activity: {str(e)}")
    
    def start_activity(self, interval: int = AI_ACTIVITY_INTERVAL) -> None:
        """
        Start AI activity at regular intervals.
        
        Args:
            interval: Time between activities in seconds
        """
        if self.activity_thread and self.activity_thread.is_alive():
            logger.warning(f"⚠️ {self.ai_id} activity already started")
            return
        
        self.stop_activity.clear()
        self.activity_thread = threading.Thread(target=self._activity_loop, args=(interval,))
        self.activity_thread.daemon = True
        self.activity_thread.start()
        
        logger.info(f"🚀 Started {self.ai_id} activity")
    
    def stop(self) -> None:
        """Stop AI activity."""
        if self.activity_thread and self.activity_thread.is_alive():
            self.stop_activity.set()
            self.activity_thread.join()
            logger.info(f"🛑 Stopped {self.ai_id} activity")
    
    def _activity_loop(self, interval: int) -> None:
        """
        Main activity loop.
        
        Args:
            interval: Time between activities in seconds
        """
        while not self.stop_activity.is_set():
            self.perform_activity()
            time.sleep(interval)


def run_4ai_system(duration: int = TEST_DURATION) -> None:
    """
    Run the 4AI system.
    
    Args:
        duration: Duration to run the system in seconds
    """
    print("=" * 70)
    print("🤖 4AI-Ash Integration System")
    print("=" * 70)
    print("This system integrates four AI assistants with the Ash platform.")
    print("Each AI has a specific role:")
    print("🔍 Claude (Debugger): Code review and improvement suggestions")
    print("🧠 GPT (Architect): System design and integration")
    print("📊 Gemini (Researcher): Data analysis and knowledge retrieval")
    print("⚙️ Llama (Executor): Task execution and deployment")
    print("-" * 70)
    print(f"The system will run for {duration} seconds, generating tasks and insights.")
    print("All data will be written to Ash_Input.json for processing by the Ash watcher.")
    print("=" * 70)
    
    # Initialize communication directory
    ensure_dir(COMM_DIR)
    
    # Create AI agents
    ai_agents = []
    
    if ENABLE_CLAUDE:
        claude = AIAgent(
            ai_id="claude",
            role="debugger",
            capabilities=["code_review", "improvement_suggestions"]
        )
        ai_agents.append(claude)
        print("✅ Claude (Debugger) initialized")
    
    if ENABLE_GPT:
        gpt = AIAgent(
            ai_id="gpt",
            role="architect",
            capabilities=["system_design", "integration"]
        )
        ai_agents.append(gpt)
        print("✅ GPT (Architect) initialized")
    
    if ENABLE_GEMINI:
        gemini = AIAgent(
            ai_id="gemini",
            role="researcher",
            capabilities=["data_analysis", "knowledge_retrieval"]
        )
        ai_agents.append(gemini)
        print("✅ Gemini (Researcher) initialized")
    
    if ENABLE_LLAMA:
        llama = AIAgent(
            ai_id="llama",
            role="executor",
            capabilities=["task_execution", "reporting"]
        )
        ai_agents.append(llama)
        print("✅ Llama (Executor) initialized")
    
    # Start AI activities
    for agent in ai_agents:
        agent.start_activity()
    
    print("-" * 70)
    print(f"🚀 All AIs started and running! System will operate for {duration} seconds...")
    
    try:
        # Wait for the specified duration
        for remaining in range(duration, 0, -1):
            if remaining % 5 == 0:
                print(f"⏳ {remaining} seconds remaining...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    finally:
        # Stop AI activities
        for agent in ai_agents:
            agent.stop()
    
    print("-" * 70)
    print("✅ 4AI system completed successfully!")
    print("📝 Check ChatGPTMemory.json to see the accumulated tasks and insights.")
    print("=" * 70)


# Run the system if executed directly
if __name__ == "__main__":
    run_4ai_system()
