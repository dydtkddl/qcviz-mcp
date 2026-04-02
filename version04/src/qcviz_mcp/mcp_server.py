"""FastMCP server bootstrap entrypoint."""

from __future__ import annotations

import logging
import importlib

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("QCViz-MCP")

# Import tool modules for registration side effects.
importlib.import_module("qcviz_mcp.tools.core")
importlib.import_module("qcviz_mcp.tools.advisor_tools")  # v5.0 advisor

if __name__ == "__main__":
    logger.info("QCViz-MCP server starting...")
    mcp.run()
