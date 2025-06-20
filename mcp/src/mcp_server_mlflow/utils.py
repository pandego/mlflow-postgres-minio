from contextlib import asynccontextmanager

from mcp_server_mlflow.server import mcp


@asynccontextmanager
async def lifespan_context(_):
    async with mcp.session_manager.run():
        yield
