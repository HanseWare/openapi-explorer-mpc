# Stateless OpenAPI Explorer MCP Server

A lightweight, stateless [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes OpenAPI/Swagger definitions to Large Language Models (LLMs) over Server-Sent Events (SSE). 

Instead of forcing an LLM to read a massive, token-heavy JSON file all at once, this server provides a suite of targeted tools. Because this server is **completely stateless**, a single running instance can explore *any* public OpenAPI definition on the fly—you just provide the URL to your AI in the chat!

## 🚀 Features & Tools

To ensure performance and prevent spamming external APIs, the server features an in-memory `LRU cache`. If the AI calls multiple tools for the same API URL in a single conversation, the server only downloads the OpenAPI definition once.

When connected, this server provides the following tools to the LLM:
* **`list_all_endpoints(openapi_url)`**: Returns a summarized list of all available endpoints (HTTP method, URL path, and short description) to help the AI discover API capabilities.
* **`get_endpoint_details(openapi_url, path)`**: Returns the exact OpenAPI specification details for a specific endpoint (e.g., `/users/{id}`), including resolved components and schemas.
* **`get_openapi_category(openapi_url, category)`**: Filters the definition and returns only the endpoints that match a specific tag/category.
* **`get_full_openapi_definition(openapi_url)`**: Returns the complete, raw OpenAPI JSON definition.

## 📦 Getting Started

Because the server is stateless, you do not need to configure any environment variables or mount any files. You simply run the container on port `8000`.

### Running via Docker

```bash
docker run -d \
  -p 8000:8000 \
  --name openapi-explorer \
  hanseware/openapi-explorer-mcp
```

## 🔌 Connecting to an MCP Client (e.g., Claude Desktop)

Since this server streams over HTTP using Server-Sent Events (SSE), you connect to it using a standard URL. 

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

## 💬 How to Use It in Chat

Once the server is connected to your AI client, you don't need to do any prior setup to explore an API. Just drop the URL directly into your prompt!

**Example Prompt:**
> *"I want to integrate with a new service. Here is their OpenAPI specification: `https://api.example.com/openapi.json`. Please use your tools to list all the available endpoints for me."*

The AI will automatically parse the URL, pass it to the `list_all_endpoints` tool, and the server will fetch, cache, and summarize the API on the fly.

## 🛠️ Local Development

If you want to build or modify the server yourself:

1. Clone this repository.
2. Install the dependencies using modern Python packaging:
   ```bash
   pip install .
   ```
3. Run the FastMCP server locally:
   ```bash
   fastmcp run server.py
   ```