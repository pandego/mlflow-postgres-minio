from fastapi import FastAPI

from mcp_server_mlflow.server import mcp
from mcp_server_mlflow.utils import lifespan_context

# Define FastAPI app and mount MCP server
app = FastAPI(
    title="Wine Quality Server",
    lifespan=lifespan_context  # Enables proper lifecycle handling
    # lifespan = lambda app: mcp.session_manager.run()
    # redirect_slashes=False,
)

app.mount(
    path="/",  # it will mount 'mcp/' into '/', so '/mcp/'
    app=mcp.streamable_http_app()
)
