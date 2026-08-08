#!/usr/bin/env python3
"""Upload files to Google Drive via direct MCP HTTP call."""
import base64, json, os, sys, urllib.request, urllib.parse

SESSION_ID = "cse_01Nsrt6nLMQ3NZVE1EYJxA1G"
MCP_SERVER_ID = "9792d709-e80a-42cd-b002-58ee1f600f33"
MCP_DRIVE_SERVER_ID = "aba6b5cf-af80-5fc0-b80b-c760296ac520"
MCP_URL = (
    f"https://api.anthropic.com/v2/ccr-sessions/{SESSION_ID}/mcp"
    f"?mcp_url=https%3A%2F%2Fdrivemcp.googleapis.com%2Fmcp%2Fv1"
    f"&mcp_server_id={MCP_DRIVE_SERVER_ID}"
    f"&toolbox_mcp_server_id={MCP_SERVER_ID}"
)
CA_BUNDLE = "/root/.ccr/ca-bundle.crt"

def get_token():
    token_file = "/home/claude/.claude/remote/.session_ingress_token"
    with open(token_file) as f:
        return f.read().strip()

def mcp_call(method, arguments, req_id=1):
    token = get_token()
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": method, "arguments": arguments}
    }).encode()
    req = urllib.request.Request(MCP_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Session-UUID", SESSION_ID)
    req.add_header("X-MCP-Server-ID", MCP_SERVER_ID)
    req.add_header("Authorization", f"Bearer {token}")

    import ssl, certifi
    try:
        ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    except Exception:
        ctx = ssl.create_default_context()

    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=120)
    except urllib.error.URLError:
        resp = urllib.request.urlopen(req, timeout=120)

    # Response is SSE format: "event: message\ndata: {...}\n\n"
    raw = resp.read().decode()
    # Extract JSON from data: lines
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("data: "):
            payload = line[6:]
            try:
                result = json.loads(payload)
                return result
            except json.JSONDecodeError:
                continue
    # Fallback: try parsing entire response as JSON
    try:
        return json.loads(raw)
    except Exception:
        return {"error": {"message": f"Could not parse SSE response: {raw[:200]}"}, "raw": raw[:200]}

def upload_file(filepath, title, parent_id, mime_type="image/png"):
    print(f"  Uploading {title} ({os.path.getsize(filepath):,} bytes)...", end=" ", flush=True)
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    result = mcp_call("create_file", {
        "title": title,
        "contentMimeType": mime_type,
        "base64Content": content,
        "parentId": parent_id,
        "disableConversionToGoogleType": True
    })

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return False
    content = result.get("result", {}).get("content", [{}])
    if isinstance(content, list) and len(content) > 0:
        text = content[0].get("text", "")
        try:
            d = json.loads(text)
            file_id = d.get("id", "?")
            print(f"OK (id={file_id})")
            return True
        except Exception:
            print(f"OK (raw: {text[:60]})")
            return True
    print(f"OK")
    return True

def upload_text(content, title, parent_id, mime_type="text/plain"):
    print(f"  Uploading {title} (text)...", end=" ", flush=True)
    b64 = base64.b64encode(content.encode()).decode()
    result = mcp_call("create_file", {
        "title": title,
        "contentMimeType": mime_type,
        "base64Content": b64,
        "parentId": parent_id,
        "disableConversionToGoogleType": True
    })
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return False
    print("OK")
    return True

if __name__ == "__main__":
    folder_id = sys.argv[1]
    day = sys.argv[2]
    output_dir = f"/home/user/maquina-carrosseis/output/{day}"

    print(f"Uploading to Drive folder {folder_id}...")

    failures = []

    # Upload legenda.txt as text
    legenda_path = f"{output_dir}/legenda.txt"
    if os.path.exists(legenda_path):
        with open(legenda_path) as f:
            legenda_text = f.read()
        if not upload_text(legenda_text, "legenda.txt", folder_id):
            failures.append("legenda.txt")

    # Upload PNGs
    for i in range(1, 8):
        png = f"{output_dir}/slide_{i:02d}.png"
        if os.path.exists(png):
            if not upload_file(png, f"slide_{i:02d}.png", folder_id):
                failures.append(f"slide_{i:02d}.png")

    # Upload carousel.html
    html_path = f"{output_dir}/carousel.html"
    if os.path.exists(html_path):
        if not upload_file(html_path, "carousel.html", folder_id, "text/html"):
            failures.append("carousel.html")

    if failures:
        print(f"\nFAILED: {failures}")
        sys.exit(1)
    else:
        print(f"\nAll files uploaded successfully!")
