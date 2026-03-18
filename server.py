import json
import os
import sys
import urllib.request
from fastmcp import FastMCP

mcp = FastMCP("OpenAPI-Explorer")

SPEC_URL = os.getenv("OPENAPI_URL")
SPEC_PATH = os.getenv("OPENAPI_FILE_PATH", "/app/openapi.json")


def load_spec():
    if SPEC_URL:
        try:
            req = urllib.request.Request(SPEC_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise RuntimeError(f"Failed to fetch OpenAPI spec from {SPEC_URL}: {e}")
    else:
        if not os.path.exists(SPEC_PATH):
            raise FileNotFoundError(f"OpenAPI spec not found at {SPEC_PATH} and OPENAPI_URL was not provided.")
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            return json.load(f)


# --- TOOL 1: Full Definition ---
@mcp.tool()
def get_full_openapi_definition() -> str:
    """Returns the complete OpenAPI JSON definition."""
    return json.dumps(load_spec(), indent=2)


# --- TOOL 2: Category Filter ---
@mcp.tool()
def get_openapi_category(category: str) -> str:
    """
    Returns a subset of the OpenAPI definition containing only the endpoints
    that match the specified category (tag).
    """
    spec = load_spec()
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
def list_all_endpoints() -> str:
    """
    Returns a summarized list of all available endpoints, including only
    the HTTP method, the URL path, and a short description. Use this to
    discover available API capabilities.
    """
    spec = load_spec()
    summary = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        if not isinstance(methods, dict): continue
        for method, details in methods.items():
            if not isinstance(details, dict): continue

            # Use 'summary' if available, otherwise fallback to 'description'
            description = details.get("summary") or details.get("description") or "No description provided."

            summary.append({
                "path": path,
                "method": method.upper(),
                "description": description
            })

    return json.dumps(summary, indent=2)


# --- TOOL 4: Specific Endpoint Details ---
@mcp.tool()
def get_endpoint_details(path: str) -> str:
    """
    Returns the full OpenAPI specification details for a single, specific
    endpoint path (e.g., '/users/{id}'). This includes all HTTP methods
    available on that path and the global components/schemas so you can
    resolve references.
    """
    spec = load_spec()
    paths = spec.get("paths", {})

    # Ensure exact match handling (sometimes APIs have trailing slashes)
    if path not in paths:
        return json.dumps({
                              "error": f"Path '{path}' not found in the OpenAPI specification. Please check the exact spelling from the list_all_endpoints tool."})

    result = {
        "openapi": spec.get("openapi", "3.0.0"),
        "info": spec.get("info", {}),
        "requested_path": path,
        "paths": {
            path: paths[path]
        },
        # We include components because the endpoint likely references schemas
        # for its request bodies and responses (e.g., $ref: '#/components/schemas/User')
        "components": spec.get("components", {})
    }

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # --- DEBUG & VALIDATION BLOCK ---
    print("Starting OpenAPI MCP Explorer...", flush=True)
    try:
        if SPEC_URL:
            print(f"Attempting to fetch OpenAPI spec from URL: {SPEC_URL}", flush=True)
        else:
            print(f"Attempting to read OpenAPI spec from local file: {SPEC_PATH}", flush=True)

        spec = load_spec()

        title = spec.get("info", {}).get("title", "Unknown API")
        version = spec.get("info", {}).get("version", "Unknown Version")
        paths_count = len(spec.get("paths", {}))

        print("✅ SUCCESS: OpenAPI specification loaded and parsed correctly!", flush=True)
        print(f"   - API Title:   {title}", flush=True)
        print(f"   - API Version: {version}", flush=True)
        print(f"   - Total Paths: {paths_count}", flush=True)
        print(f"   - Tools Registered: 4", flush=True)

    except Exception as e:
        print(f"❌ FATAL ERROR: Could not load OpenAPI specification on startup.", flush=True)
        print(f"   Details: {e}", flush=True)
        print("Exiting container to prevent runtime failures.", flush=True)
        sys.exit(1)
        # --------------------------------

    print("\nStarting SSE server on 0.0.0.0:8000...", flush=True)
    mcp.run(transport="sse", host="0.0.0.0", port=8000)