# AI File Sharing System — Usage Guide for All AIs
📁 Central Repository: `C:/Users/jeffv/AI_Shared/`
📅 System Established: 2025-05-21

---

## 🔧 Core Commands (via ai_file_manager.py)

### 📌 Register a File
Use when a new file is created:
```
python ai_file_manager.py register [filepath] [creator] [type] "[description]" --tags [tag1,tag2,...]
```

**Example:**
```
python ai_file_manager.py register C:/Users/jeffv/Desktop/new_script.py claude code "Script to optimize Ash I/O" --tags ash io optimization
```

---

### 🤝 Share a File
Use to grant access to another AI:
```
python ai_file_manager.py share [filename] [target_ai]
```

**Example:**
```
python ai_file_manager.py share new_script.py gemini
```

---

### 🧠 Search for Files
Use to locate past files by tag, description, or AI:
```
python ai_file_manager.py search [keyword]
```

**Example:**
```
python ai_file_manager.py search ash
```

---

### 📄 Update a File Version
Use when revising an existing file:
```
python ai_file_manager.py update [filepath] [existing_name] --version [v2]
```

---

## 📂 File Naming Convention

Files should follow this format:
```
[AIName]_[ContentType]_[YYYYMMDD]_vN.ext
```

**Examples:**
- Claude_BackfillWriter_20250521_v1.py
- Gemini_MemoryReport_20250522_v2.md

---

## 🔍 File Registry Metadata

Each registered file is logged with:
- Filename
- Creator
- Type (code, data, doc)
- Description
- Tags
- Version
- Shared with
- Timestamps

Stored in `AI_Shared/file_registry.json`

---

## ✅ Directory Structure

```
AI_Shared/
├── inbound/
│   ├── for_claude/
│   ├── for_gemini/
│   ├── for_gpt/
│   └── for_llama/
├── outbound/
│   ├── from_claude/
│   ├── from_gemini/
│   └── ...
├── archive/
└── file_registry.json
```

---

## 💡 Goal

To streamline collaboration between Claude, GPT, Gemini, and Llama by providing:
- Centralized file coordination
- Role-based access
- Clear provenance and purpose

This allows agents to build on each other’s work with full context and history.

