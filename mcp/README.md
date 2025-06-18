# 🧪 MCP Wine Quality Server

This MCP server exposes a machine learning model (served via MLflow) to predict wine quality based on its chemical properties.
> ⚠️ This README assumes the mlflow server is running locally, as defined [here](../README.md#511-using-uv-recommended), ***Section 5.1.1 Using `uv`***.

This tutorial implements the [Model Context Protocol](https://modelcontextprotocol.org/) and provides:
- 🛠 A tool: `predict_wine_quality` — calls the MLflow model
- 📄 A resource: `wine://example` — shows a valid input payload
- ✏️ A prompt: `format_predictions` — formats predictions into Markdown

---

## 🧰 Features

- ✅ Built using [`fastmcp`](https://github.com/modelcontextprotocol/python-sdk)
- ✅ Batch prediction via MLflow `dataframe_split`
- ✅ Fully compatible with Claude Desktop or any MCP-compatible host
- ✅ Runs locally via `uv` or in Docker

---

## 🚀 Quick Start
### 1. Test run locally via CLI (stdio)
- This following command will run the server with a GUI in stdio mode:
  ```bash
  mcp dev src/mcp_server_mlflow/server.py
  ```

### 2. *Optional:* Install it in Claude Desktop
- You can install the server *automatically* using the `mcp install` command:
  ```bash
  uv sync && source .venv/bin/activate
  mcp install src/mcp_server_mlflow/server.py --name "My Wine Quality Server (auto)"
  ```
  > 💡 I would still recommend adding the configuration *manually* (see below in **Claude Desktop Integration**).

---

### 3. Setup the Server to be used by the Host
In this section, I will use **Claude Desktop** as an example, but you can use any MCP-compatible host.

#### 🐳 Using Docker:

- If you prefer to use `docker` instead (probably safer), you will need to build the image first:
  ```bash
  docker build -t mcp/wine .
  ```

- Once the image is built, add the following configuration to your `claude_desktop_config.json`:
  ```json
    {
      "mcpServers": {
        "My Wine Quality Server (docker)": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "--init",
            "mcp/wine"
          ]
        }
      }
    }
    ```
---

#### 🐍 Using `uv`:
- You will need to have `uv` installed. Then add the following configuration to your `claude_desktop_config.json`:
  ```json
        {
        "mcpServers": {
          "My Wine Quality Server (uv)": {
            "command": "uv",
            "args": [
              "--directory",
              "/PATH-TO-THIS-REPO/mlflow-postgres-minio/mcp",
              "run",
              "mcp-server-mlflow"
            ]
          }
        }
      }
  ``` 
  > If your `uv` is not installed globally, you need to replace `"command": "uv"` with the absolute path to `uv`, for example `"command": "/PATH-TO-THIS-REPO/mlflow-postgres-minio/mcp/.venv/bin/uv"`

---

## 🚀 Talk to Claude (the Host) about Wine Quality

- Open **Claude Desktop** and check if `My Wine Quality Server` is listed in the `Tools` section.
- You can now ask *Claude* to predict the quality of some wine. Here's a simple example of a *prompt*:
  ```txt
  Hey genius grape whisperer!
  
  I've got two bottles of wine here, and I need your ultra-intelligent opinion because my taste buds have trust issues.

  Mystery Wine 1:
    * Fixed acidity: 11.6
    * Volatile acidity: 0.58
    * Citric acid: 0.66
    * Residual sugar: 2.2
    * Chlorides: 0.074
    * Free sulfur dioxide: 10
    * Total sulfur dioxide: 47
    * Density: 1.0008
    * pH: 3.25
    * Sulphates: 0.57
    * Alcohol: 9%
  
  Mystery Wine 2:
    * Fixed acidity: 7.4
    * Volatile acidity: 0.36
    * Citric acid: 0.3
    * Residual sugar: 1.8
    * Chlorides: 0.074
    * Free sulfur dioxide: 17
    * Total sulfur dioxide: 24
    * Density: 0.99419
    * pH: 3.24
    * Sulphates: 0.7
    * Alcohol: 11.4%
  
  So tell me: which of these liquid mood enhancers is the superior sip?
  Or are they both just glorified vinegar in disguise?
  Be honest. Be brutal. Be wine-wise. 🍇🍷
  ```

## 🧪 Available Endpoints

| Type      | Name                   | Description                         |
|-----------|------------------------|-------------------------------------|
| Tool      | `predict_wine_quality` | Predicts wine quality from features |
| Resource  | `wine://example`       | Sample input payload (JSON)         |
| Prompt    | `format_predictions`   | Markdown formatter for results      |

---

## 🧼 Development Tips

### Run tests:
- Run the following command:
  ```bash
  pytest
  ```

### Lint with ruff:
- Run the following command:
  ```bash
  ruff check src
  ```

---

## 📁 Project Structure

```
mcp/
├── pyproject.toml
├── Dockerfile
├── uv.lock
└── src/
    └── mcp_server_mlflow/
        ├── __init__.py
        ├── __main__.py
        └── server.py
```

---

## License

MIT 👉 see `LICENSE`

---

Made with 💙 by [`pandego`](https://github.com/pandego)
