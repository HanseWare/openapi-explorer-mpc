# OpenAPI Explorer MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes OpenAPI/Swagger definitions to Large Language Models (LLMs) over Server-Sent Events (SSE). 

Instead of forcing an LLM to read a massive, token-heavy JSON file all at once, this server provides a suite of targeted tools. This allows the AI to read a "table of contents" of your API and zoom in on specific endpoints, saving tokens, reducing context window fatigue, and improving accuracy.

## 🚀 Features (Available Tools)

When connected, this server provides the following tools to the LLM:
* **`list_all_endpoints`**: Returns a summarized list of all available endpoints (HTTP method, URL path, and a short description) to help the AI discover API capabilities.
* **`get_endpoint_details`**: Takes a specific path (e.g., `/users/{id}`) and returns the exact OpenAPI specification details for just that endpoint, including resolved components/schemas.
* **`get_openapi_category`**: Filters the OpenAPI definition and returns only the endpoints that match a specific tag/category.
* **`get_full_openapi_definition`**: Returns the complete, raw OpenAPI JSON definition.

## 📦 Getting Started

The server is distributed as a Docker image and runs as a background web server on port `8000`. You can point it to a remote URL or mount a local file.

### Option A: Using a Remote OpenAPI URL (Recommended)

If your OpenAPI definition is hosted online, simply pass the URL via the `OPENAPI_URL` environment variable:

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAPI_URL="https://your-domain.com/openapi.json" \
  --name openapi-explorer \
  hanseware/openapi-explorer-mcp
```

### Option B: Using a Local OpenAPI File

If you have a local `openapi.json` file, mount it into the container at `/app/openapi.json`:

```bash
docker run -d \
  -p 8000:8000 \
  -v /absolute/path/to/your/openapi.json:/app/openapi.json \
  --name openapi-explorer \
  hanseware/openapi-explorer-mcp
```

### Startup Validation

The container features a "fail-fast" startup script. You can verify that it successfully downloaded and parsed your OpenAPI definition by checking the Docker logs immediately after starting it:

```bash
docker logs openapi-explorer
```
*If successful, you will see the API Title, Version, and the total number of paths parsed.*

## 🔌 Connecting to an MCP Client (e.g., Claude Desktop)

Because this server streams over HTTP using Server-Sent Events (SSE), you connect to it using a standard URL. 

Add the following to your MCP client configuration file (for Claude Desktop, this is usually `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "openapi-explorer": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```
*(Make sure the Docker container is running before attempting to use the tools in your AI client).*

## 🛠️ Local Development

If you want to build or modify the server yourself:

1. Clone this repository.
2. Install the dependencies using modern Python packaging:
   ```bash
   pip install .
   ```
3. Run the FastMCP server locally:
   ```bash
   OPENAPI_URL="https://your-domain.com/openapi.json" fastmcp run server.py
   ```