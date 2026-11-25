# python/m5/sales_assistant/agent.py
"""Chinook Sales Assistant.

Uses a local FilesystemBackend, a QuickJS code interpreter for arithmetic
and data prep, and a dedicated chart tool for rendering.

Start with:
    ./start.sh
"""

from __future__ import annotations  # postpones evaluating type annotations, making forward references easier

import logging  # allows an application to record what is happening while it runs.
import os   # allows python to interact with the OS e.g. get cwd os.getcwd(), check file exists os.path.exists("config.py")
from pathlib import Path    # library for working with file and directory paths > manipulate file paths as objects rather than as ordinary strings

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_mcp_adapters.client import MultiServerMCPClient          # turns server tools into LangChain tools
from langchain_mcp_adapters.sessions import StreamableHttpConnection    # connection mechanism for remote servers
from langchain_quickjs import CodeInterpreterMiddleware
from subagents import build_subagents
from tools.chart import render_pie_chart
from tools.html import markdown_to_html

from models import strong_model

logger = logging.getLogger(__name__) # creates a logger associated with the current module; to identify exactly where each log message originated

HERE = Path(__file__).resolve().parent # Find the absolute location of the current python file, then give me the directory containing that file.
# __file__ : A special python variable containing the path to the current python file. from /home/.../agent.py
# Path(__file__) : Converts file path into a 'Path' object
# .resolve() : Resolves the path into an absolute path; Path("agents/researcher.py").resolve() >> /home/kaleb/gtmx/agents/researcher.py
# .parent : Returns the directory containing the file; Path("/home/kaleb/gtmx/agents/researcher.py").parent >> /home/kaleb/gtmx/agents

SYSTEM_PROMPT = (
    "You are a sales assistant for Jane Peacock, a Sales Support Agent at "
    "Chinook, an online music distributor. Follow your operating manual (loaded " 
    "from your memory) and use the matching playbook from /skills/ for each task."
)

MAIL_SERVER: StreamableHttpConnection = {   # a server dictionary with 'transport' and 'url'
    "transport": "streamable_http", 
    "url": "http://127.0.0.1:5002/mcp"
}

_enable_search = bool(os.environ.get("TAVILY_API_KEY"))
if not _enable_search:
    logger.info("TAVILY_API_KEY not set — newsletter research subagent disabled.")

_backend = FilesystemBackend(root_dir=str(HERE), virtual_mode=True)     
# reads and writes files on the local disk, scoped to a 'root_dir' you specify. Used when agent should work with real files in a local directory

async def make_graph():
    # MCP
    client = MultiServerMCPClient({"mock-mail": MAIL_SERVER})
    mail_tools = await client.get_tools() # retrieves all tools as 'BaseTool' objects.
    #
    return create_deep_agent(
        model=strong_model,
        tools=[markdown_to_html, render_pie_chart],
        system_prompt=SYSTEM_PROMPT,
        subagents=build_subagents(_backend, enable_search=_enable_search, mail_tools=mail_tools),
        skills=["/skills"],
        memory=["/AGENTS.md"],
        backend=_backend,
        middleware=[CodeInterpreterMiddleware()],
        name="chinook-sales-assistant",
    ).with_config({"recursion_limit": 50})
