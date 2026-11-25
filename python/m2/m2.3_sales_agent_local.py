"""Local stand-in for m2.3_sales_agent.py.

Same lesson — a data analyst agent working against the Chinook database and
producing a chart — but using `LocalShellBackend` instead of a LangSmith
Sandbox (Sandboxes require an Enterprise plan).

Instead of `backend.upload_files()`, the database is copied into the local
workspace, and the chart is copied back out at the end.

WARNING: LocalShellBackend has no isolation — commands run as your user.

RUN
  cd python
  uv run ./m2/m2.3_sales_agent_local.py
  open m2/genre_revenue_local.png
"""

import shutil
import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from models import model

DB_PATH = Path(__file__).resolve().parent / "chinook.db"

workspace = Path(tempfile.mkdtemp(prefix="lca-deepagents-lab-"))
print(f"Workspace: {workspace}")

shutil.copy(DB_PATH, workspace / "chinook.db")

backend = LocalShellBackend(
    root_dir=workspace,
    virtual_mode=False,
    inherit_env=True,
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    system_prompt=(
        "You are a sales data analyst with access to the Chinook music store "
        "database at chinook.db in your working directory. Use sqlite3 and "
        "matplotlib to answer questions with charts. matplotlib is already "
        "installed, so do not install anything. Use relative paths "
        "(e.g. chinook.db, genre_revenue.png), never absolute paths. "
        "When asked to produce a chart, write a Python script, execute it, "
        "and confirm the output file was created."
    ),
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Query the Chinook database at chinook.db to get total revenue "
                    "by genre. Create a clean donut chart showing each genre's share "
                    "of total sales revenue. Group any genres that individually "
                    "account for less than 3% of total revenue into a single 'Other' "
                    "slice. Label each slice with the genre name and percentage. "
                    "Use a visually distinct color palette, leave a white center hole, "
                    "and make sure no labels overlap with each other or with the title. "
                    "Add enough top padding so the title is fully visible. "
                    "Save the chart to genre_revenue.png."
                ),
            }
        ]
    }
)
print(result["messages"][-1].text)

out_path = Path(__file__).parent / "genre_revenue_local.png"
shutil.copy(workspace / "genre_revenue.png", out_path)
print(f"Chart saved to {out_path}")
