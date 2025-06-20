# 🧪 MCP Wine Quality Server

This MCP server exposes a machine-learning model (served via **MLflow**) to predict wine quality from its chemical properties.

> ⚠️ This README assumes your MLflow inference server is running locally as described in the project-root [`README.md`](../README.md#511-using-uv-recommended), ***Section 5.1.1***.

The server demonstrates the [Model Context Protocol](https://modelcontextprotocol.org/) primitives:

| Primitive | Name | Purpose |
|-----------|------|---------|
| 🛠 Tool | `predict_wine_quality` | Calls the MLflow model |
| 📄 Resource | `wine://example` | Shows a valid input payload |
| ✏️ Prompt | `format_predictions` | Formats predictions as Markdown |

---

## 🧰 Features

* Built with [`fastmcp`](https://github.com/modelcontextprotocol/python-sdk)
* Batch prediction via MLflow's `dataframe_split`
* Works with Claude Desktop or **any** MCP-compatible host
* Runs locally with **uv** or fully containerised with **Docker**
* ***(Optional)*** **Streamable-HTTP** & **FastAPI** wrappers for remote hosting

---

## 🚀 Quick Start

### 1 - Setup the environment with `uv`:
- I'll use `uv` to manage the environment, but you can use `venv` or `conda` if you prefer:
  ```bash
  uv venv && source .venv/bin/activate && uv sync
  ```

### 2 - Run locally in `stdio` mode
- A good way to test the server is by opening a GUI for quick inspection:
  ```bash
  mcp dev src/mcp_server_mlflow/server.py
  ```

### 3 - (Optional) Automatically install in Claude Desktop
- If you want to install the server in Claude Desktop, you can use the following command:
  ```bash
  mcp install src/mcp_server_mlflow/server.py --name "My Wine Quality Server"
  ```
  > 💡 Manual config is still recommended for clarity - see **Claude Desktop Integration** below.

---

## 🖥️ Claude Desktop Integration (`stdio`)

Below are two proven ways to launch the server from Claude.

### 🐳 Docker (recommended isolation)
- Build once:
  ```bash
  docker build -t mcp/wine .
  ```

- Add to `claude_desktop_config.json`:
  ```jsonc
  {
    "mcpServers": {
      "My Wine Quality Server (docker)": {
        "command": "docker",
        "args": ["run","-i","--rm","--init","mcp/wine"]
      }
    }
  }
  ```

### 🐍 uv (virtual-env dev)
- If you want to install the server in Claude Desktop, you can use the following command:
  ```jsonc
  {
    "mcpServers": {
      "My Wine Quality Server (uv)": {
        "command": "uv",
        "args": [
          "--directory",
          "/ABS/PATH/TO/REPO/mcp",
          "run",
          "mcp-server-mlflow"
        ]
      }
    }
  }
  ```
  > Replace the path and, if `uv` isn't global, use the full executable path.

---

## 🌐 Exposing the Server over HTTP (`streamable-http`)

Sometimes you need a **remote** MCP endpoint (e.g., cloud agents, multi-user access). The project ships two variants:

| Variant | Entrypoint | Dockerfile | Default port |
|---------|------------|------------|--------------|
| **Streamable-HTTP** | `mcp_server_mlflow.http_server` | `Dockerfile_http` | `8000` |
| **FastAPI wrapper** | `mcp_server_mlflow.fastapi_server:app` | `Dockerfile_fastapi` | `8000` |

### A - Streamable-HTTP (bare, no FastAPI)
- Here's a simple example:
  ```python
  # http_server.py
  
  from mcp_server_mlflow.server import mcp
  
  if __name__ == "__main__":
      mcp.run(
          transport="streamable-http",
          host="0.0.0.0",
          port=8000,
          mount_path="/mcp"
      )
  ```

- Build & expose:
  ```bash
  docker build -t mcp/wine-http -f Dockerfile_http .
  docker run -p 8000:8000 mcp/wine-http
  ```

### B - FastAPI wrapper (mounts MCP app)
- Here's a simple example:
  ```python
  # fastapi_server.py
  
  from fastapi import FastAPI
  from mcp_server_mlflow.server import mcp
  from mcp_server_mlflow.utils import lifespan_context  # or lambda app: mcp.session_manager.run()
  
  app = FastAPI(title="Wine Quality Server", lifespan=lifespan_context)
  app.mount("/", mcp.streamable_http_app())  # mounts the '/mcp' at the root path '/', so it answers at '/mcp'
  ```

- Build & expose:
  ```bash
  docker build -t mcp/wine-fastapi -f Dockerfile_fastapi .
  docker run -p 8000:8000 mcp/wine-fastapi
  ```

👉 Both variants answer at `http://<host>:8000/mcp`.

---

### 🔬 Test the HTTP endpoint
- You can use `curl` to test the endpoint, but be sure to use `/mcp/` at the end of the URL:
  ```bash
  curl -X POST http://localhost:8000/mcp/ \
      -H "Content-Type: application/json" \
      -H "Accept: application/json, text/event-stream" \
      -d '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "predict_wine_quality",
        "arguments": {
          "inputs": [[7.4,0.7,0,1.9,0.076,11,34,0.9978,3.51,0.56,9.4]],
          "columns": ["fixed acidity","volatile acidity","citric acid","residual sugar",
                      "chlorides","free sulfur dioxide","total sulfur dioxide",
                      "density","pH","sulphates","alcohol"]
        }
      }
    }'
  ```

- You should receive a streamed JSON-RPC response:
  ```text
  event: message
  data: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"5.14"}],"isError":false}}
  ```

---

### 🛠️ Using HTTP servers with Claude Desktop (proxy needed)

Claude Desktop currently launches **stdio** servers only 👉 [discussion](https://github.com/orgs/modelcontextprotocol/discussions/16).

- To use your HTTP instance, insert a small adapter such as this popular open-source proxy 👉 [`mcp-stdio-to-streamable-http-adapter`](https://github.com/pyroprompts/mcp-stdio-to-streamable-http-adapter):

  ```jsonc
  {
    "mcpServers": {
      "wine-quality-http": {
        "command": "npx",
        "args": ["@pyroprompts/mcp-stdio-to-streamable-http-adapter"],
        "env": {
          "URI": "http://localhost:8000/mcp",
          "MCP_NAME": "wine-quality-http"
        }
      }
    }
  }
  ```
  > 💡 The proxy speaks stdio to Claude and Streamable-HTTP to your server.

---

## 🧪 Available Endpoints

| Type | Name | Description |
|------|------|-------------|
| Tool | `predict_wine_quality` | Predicts wine quality |
| Resource | `wine://example` | Sample JSON payload |
| Prompt | `format_predictions` | Formats results |

---

## 🧼 Development Tips
* **Tests** `pytest .`
* **Lint** `ruff check src`

---

## 📁 Project Structure
```
mcp/
├─ pyproject.toml
├─ Dockerfile
├─ Dockerfile_http
├─ Dockerfile_fastapi
└─ src/
   └─ mcp_server_mlflow/
       ├─ server.py
       ├─ http_server.py
       └─ fastapi_server.py
```

---

## License
MIT - see `LICENSE`

Made with 💙 by [@pandego](https://github.com/pandego)
