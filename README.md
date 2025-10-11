# 🧭 Project Integration Guide

This document explains **how to correctly merge and extend** the project
without breaking the workflow or the shared state system.

Please **read carefully before pushing any changes**.

---

## 🧩 1. Clone and Setup

Before modifying anything, make sure you can run the base version.

```bash
git pull origin Fei/PdfAgent
pip install -r requirements.txt
streamlit run main.py
```

If the Streamlit app shows “PDF Agent” and you can upload a file,
your environment is working correctly.

---

## ⚙️ 2. System Overview

The project follows a modular **graph-based workflow**:

```
Node  →  Subgraph  →  Tool  →  Graph  →  Streamlit UI
```

| Component        | Role                                 | Path                                    |
| ---------------- | ------------------------------------ | --------------------------------------- |
| Node             | Smallest processing unit             | `backend/nodes/web_node`                |
| Subgraph         | Groups related nodes                 | `backend/pipeline/web_tool`             |
| Tool             | Implements logic / external function | `tools/aqeel_tool`                      |
| Tool Registry    | Central tool mapping                 | `backend/pipeline/get_tool_registry.py` |
| Graph Invocation | Build and execute                    | `home_ui.py`                            |
| App Entry        | Streamlit app                        | `main.py`                               |

---

## 🧱 3. The State System Explained

The app uses a centralized **memory state** to manage all information flow.

- **Global Memory**:
  Managed by Streamlit via `st.session_state.state`
  (this persists across reruns and user interactions)

- **Graph State** (`GraphState` class):
  Holds all runtime data passed between nodes, subgraphs, and tools.
  Each tool can extend it safely with new fields.

---

### 🔧 How to Extend GraphState

If your tool needs new data fields (e.g., `user_profile`, `weather_info`, etc.),
add them directly to the `GraphState` model.

**File:**
`backend/model/states/GraphState.py`

**Example:**

```python
from pydantic import BaseModel

class GraphState(BaseModel):
    qa_state: dict = {}
    graph_config: dict = {}
    logs: list = []
    messages: list = []

    # Add your custom fields here
    user_profile: dict = {}
    weather_info: dict = {}
```

You can then access and modify them inside your tool:

```python
state.user_profile.name = "John"
```

✅ This is safe — Streamlit automatically stores it inside `st.session_state.state`,
so your data will persist across UI interactions.

---

## 🧠 4. Adding Your Tool

Each developer should create their own **tool class** under `tools/`.

### Step 1. Create your tool

**File:** `tools/my_new_tool.py`

```python
from backend.model.return_types import ToolReturnClass

class MyNewTool:
    def __init__(self, qa_state):
        self.qa_state = qa_state

    def run(self):
        # Example: use your custom state field
        user_name = self.qa_state.user_profile.get("name", "unknown user")

        response = f"Hello {user_name}, this is my new tool."
        self.qa_state.messages.ai_response_list.append(response)

        return ToolReturnClass(
            state=self.qa_state,
            agent_response=response,
            meta={"tool_name": "my_new_tool"}
        )
```

---

### Step 2. Register your tool

Open `backend/pipeline/get_tool_registry.py`
and add your class to the registry:

```python
from tools.my_new_tool import MyNewTool

def get_tool_registry():
    return {
        "qa_tool": QaTool,
        "my_new_tool": MyNewTool,  # <- add here
    }
```

---

### Step 3. Verify Execution

Run the app again:

```bash
streamlit run main.py
```

Then check the sidebar logs — you should see:

```
[tool_name: my_new_tool] executed successfully
```

If it appears, your integration worked 🎉

---

## 🔍 5. Input / Output Rules

To keep the framework stable, follow these key rules:

| Rule                                                               | Why it matters                                                 |
| ------------------------------------------------------------------ | -------------------------------------------------------------- |
| ✅ Each tool must **return a `ToolReturnClass`**                   | So the graph can propagate results                             |
| ✅ Use or extend `GraphState` for all state data                   | Ensures compatibility with Streamlit memory                    |
| ✅ Never mutate `state` directly — use `.copy()` when needed       | Prevents side effects in graph flow                            |
| ✅ Match input/output key names                                    | Graph depends on these to route correctly                      |
| ⚠️ Don’t rename existing fields (`qa_state`, `graph_config`, etc.) | Will break dependent nodes                                     |
| ⚙️ You can add _new_ fields freely                                 | As long as you update both GraphState and your ToolReturnClass |

---

## 🧩 6. How Memory Works

- The whole runtime memory is stored in:

  ```python
  st.session_state.state  # type: GraphState
  ```

- Each time you run a tool, its updates are synced automatically.
- You can treat this like a global context:
  all nodes, subgraphs, and tools share it.

> ⚠️ In short: you can “do whatever you want” inside your tool,
> as long as your **input keys and return structure** match
> what’s expected in `GraphState` and `ToolReturnClass`.

---

## ✅ 7. Before Commit Checklist

- [ ] Can run `streamlit run main.py` without error
- [ ] Your tool is registered in `get_tool_registry.py`
- [ ] Any new state fields are added to `GraphState`
- [ ] You return a valid `ToolReturnClass`
- [ ] No direct file merges — use imports or registry
- [ ] Logs confirm your tool executed

---

## 💬 Final Note

This project uses a **stateful, modular architecture**.
Each person can extend it without breaking others —
just follow the data flow and state schema.
