from mcp_server_mlflow.server import mcp


def main():
    """CLI entrypoint for MCP Server in StdIO mode."""
    mcp.run(
        transport="stdio"
    )
