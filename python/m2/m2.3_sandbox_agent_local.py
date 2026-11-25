"""Local stand-in for m2.3_sandbox_agent.py.

LangSmith Sandboxes need an Enterprise plan, so `SandboxClient.create_sandbox()`
returns 403 "Sandbox feature is not enabled for this organization". This version
keeps the same lesson (agent writes a script to a file, then executes it) but
runs the shell in a throwaway directory on your machine instead.

WARNING: LocalShellBackend has no isolation — commands run as your user.

RUN
  cd python
  uv run ./m2/m2.3_sandbox_agent_local.py
"""

import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from models import model

workspace = Path(tempfile.mkdtemp(prefix="lca-deepagents-lab-"))
print(f"Workspace: {workspace}")

backend = LocalShellBackend(
    root_dir=workspace,
    virtual_mode=False,
    inherit_env=True,
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    system_prompt=(
        "You are a coding assistant. When asked to run code, write the script "
        "to a file first, then execute it. Show the output in your final answer. "
        f"Your working directory is {workspace}. Use relative paths (e.g. fib.py), "
        "never absolute paths."
    ),
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Write a Python script that prints the first 15 Fibonacci numbers, "
                    "save it to fib.py, and run it."
                ),
            }
        ]
    }
)
print(result["messages"][-1].text)
