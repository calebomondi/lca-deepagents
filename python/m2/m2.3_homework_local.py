"""Local stand-in for m2.3_homework.py.

Same lesson — prove that the backend's filesystem persists between two
`invoke()` calls on the same agent — but using `LocalShellBackend` instead of a
LangSmith Sandbox (Sandboxes require an Enterprise plan).

The TODOs are filled in with the reference answers; edit them freely.

WARNING: LocalShellBackend has no isolation — commands run as your user.

RUN
  cd python
  uv run ./m2/m2.3_homework_local.py
  open m2/homework_chart_local.png
"""

import shutil
import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from models import model

# TODO 1 filled in
SYSTEM_PROMPT = (
    "You are a data visualization assistant. When asked to run code, "
    "write the script to a file first, then execute it. matplotlib is "
    "already installed, so do not install anything. When asked for a "
    "chart, use matplotlib and save it as a .png file. "
    "Use relative paths (e.g. rainfall.json, chart.png), never absolute paths."
)

# TODO 2 filled in
TASK_ONE = (
    "Generate 12 months of made-up monthly rainfall totals (in mm) for "
    "a fictional city, save them to rainfall.json, and print them."
)
TASK_TWO = (
    "Read rainfall.json (don't regenerate the numbers) and create a bar "
    "chart of monthly rainfall. Save it to chart.png."
)

# TODO 3 filled in: path relative to the backend's workspace
CHART_PATH = "chart.png"

workspace = Path(tempfile.mkdtemp(prefix="lca-deepagents-homework-"))
print(f"Workspace: {workspace}")

backend = LocalShellBackend(
    root_dir=workspace,
    virtual_mode=False,
    inherit_env=True,
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    system_prompt=SYSTEM_PROMPT,
)

result = agent.invoke({"messages": [{"role": "user", "content": TASK_ONE}]})
print("--- Task 1 ---")
print(result["messages"][-1].text)

result = agent.invoke({"messages": [{"role": "user", "content": TASK_TWO}]})
print("\n--- Task 2 (same backend, should see Task 1's file) ---")
print(result["messages"][-1].text)

src = workspace / CHART_PATH
out_path = Path(__file__).parent / "homework_chart_local.png"
shutil.copy(src, out_path)
print(f"Chart saved to {out_path}")
