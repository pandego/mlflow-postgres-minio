from mcp_server_mlflow.server import mcp

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        mount_path="/mcp",
    )
