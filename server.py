import json
import urllib.request
from functools import lru_cache
from fastmcp import FastMCP, Context
import os

mcp = FastMCP("Stateless-OpenAPI-Explorer")


# Cache the last 10 downloaded specs so sequential tool calls are instant
@lru_cache(maxsize=10)
def load_spec(openapi_url: str):
    try:
        req = urllib.request.Request(openapi_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        raise RuntimeError(f"Failed to fetch OpenAPI spec from {openapi_url}: {e}")

APP_NAME = os.getenv("APP_NAME", "some-mcp-server")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = """
This is a FastMCP (3.1.1) server that provides tools to explore any OpenAPI specification URL provided by the AI client."""

@mcp.resource(
    "resource://mcp-gallery-info",
    name="MCPGalleryInfo",
    description="Stellt grundlegende Informationen über den MCP-Server bereit. Diese Ressource dient als Datenquelle für die MCP-Gallery.")
async def get_mcp_gallery_info(ctx: Context) -> str:
    """
    Stellt grundlegende Informationen über den MCP-Server bereit.
    Diese Ressource dient als Einstiegspunkt für die MCP-Galerie.
    """
    await ctx.debug(f"Abruf von mcp_gallery_info, request_id: {ctx.request_id}")
    payload = {
        "server_name": mcp.name,
        "server_version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "required_api_keys": [

        ],
        "authors": [
            "Max Sternitzke"
            "Patrick Willnow"
        ],
        "contact_info": {
            "email": "ai-services.mylab@th-luebeck.de",
            "phone": "+49 451 300-5818",
            "website": "https://mylab.th-luebeck.de/"
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=4)

# --- TOOL 1: Full Definition ---
@mcp.tool()
def get_full_openapi_definition(openapi_url: str) -> str:
    """Returns the complete OpenAPI JSON definition from the provided URL."""
    return json.dumps(load_spec(openapi_url), indent=2)


# --- TOOL 2: Category Filter ---
@mcp.tool()
def get_openapi_category(openapi_url: str, category: str) -> str:
    """
    Returns a subset of the OpenAPI definition containing only the endpoints
    that match the specified category (tag) from the provided URL.
    """
    spec = load_spec(openapi_url)
    filtered_paths = {}
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        if not isinstance(methods, dict): continue
        for method, details in methods.items():
            if not isinstance(details, dict): continue
            tags = details.get("tags", [])
            if any(t.lower() == category.lower() for t in tags):
                if path not in filtered_paths:
                    filtered_paths[path] = {}
                filtered_paths[path][method] = details

    result = {
        "openapi": spec.get("openapi", "3.0.0"),
        "info": spec.get("info", {}),
        "requested_category": category,
        "paths": filtered_paths,
        "components": spec.get("components", {})
    }
    return json.dumps(result, indent=2)


# --- TOOL 3: Endpoint Summary List ---
@mcp.tool()
def list_all_endpoints(openapi_url: str) -> str:
    """
    Returns a summarized list of all available endpoints from the provided URL,
    including only the HTTP method, the URL path, and a short description.
    Use this to discover available API capabilities.
    """
    spec = load_spec(openapi_url)
    summary = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        if not isinstance(methods, dict): continue
        for method, details in methods.items():
            if not isinstance(details, dict): continue

            description = details.get("summary") or details.get("description") or "No description provided."

            summary.append({
                "path": path,
                "method": method.upper(),
                "description": description
            })

    return json.dumps(summary, indent=2)


# --- TOOL 4: Specific Endpoint Details ---
@mcp.tool()
def get_endpoint_details(openapi_url: str, path: str) -> str:
    """
    Returns the full OpenAPI specification details for a single, specific
    endpoint path (e.g., '/users/{id}') from the provided URL. This includes
    all HTTP methods available on that path and the global components.
    """
    spec = load_spec(openapi_url)
    paths = spec.get("paths", {})

    if path not in paths:
        return json.dumps({
                              "error": f"Path '{path}' not found in the OpenAPI specification at {openapi_url}. Please check the exact spelling from the list_all_endpoints tool."})

    result = {
        "openapi": spec.get("openapi", "3.0.0"),
        "info": spec.get("info", {}),
        "requested_path": path,
        "paths": {
            path: paths[path]
        },
        "components": spec.get("components", {})
    }

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    print("Starting Stateless OpenAPI MCP Explorer on 0.0.0.0:8000...", flush=True)
    print("Ready to process any OpenAPI URL provided by the AI client.", flush=True)
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)