import os
import json
from datetime import datetime

# Load data
with open("final_brain_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Paths
core_path = "seraphis_final_core.md"

# Build memory block
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
memory_block = f"""---  
🧠 **New Query Recorded** – {timestamp}  
**Query:** {data['query']}  
**Final Answer:** {data['final_answer']}  
**Reasoning Summary:** {data['reasoning_summary']}  

**Chunks Used:**  
{json.dumps(data['used_chunks'], indent=2, ensure_ascii=False)}  
---\n
"""

# Check for duplication (optional logic – upgrade later)
with open(core_path, "a", encoding="utf-8") as f:
    f.write(memory_block)

print("✅ New memory block added to seraphis_final_core.md")
