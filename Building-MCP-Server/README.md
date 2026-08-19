# Build and Host an MCP Server

A tiny, beginner-friendly **MCP server** that exposes our Episode-2 diagnostic tools over a standard protocol — so *any* AI agent (or Claude Desktop, or an IDE) can discover and call them.

This is the companion code for **Episode 3** of the **DevOps & Data Simplified — AI** series. In Episode 2 our diagnostic tool was welded *inside* one agent's script. Here we lift it out into a standalone service.

---

## The one idea

MCP (the **Model Context Protocol**) is a standard way to hand tools and data to AI models — think of it as the **USB-C port for AI tools**. You build your tool once, speak MCP, and any MCP-aware client can plug in and use it.

And building one is almost all plain Python:

> **You write the function; the SDK handles the protocol.**

---

## What's inside `server.py`

| Section | What it does |
|---------|--------------|
| **Setup** | Creates the server (`MCPServer(...)`) and defines the safety constants (allowlist, forbidden chars, timeout) |
| **`_safe_run`** | The guardrail engine — the exact allowlist logic from Episode 2, now shared by both tools |
| **Tool 1: `run_command`** | Runs a read-only shell command; `@mcp.tool()` exposes it over MCP |
| **Tool 2: `list_top_processes`** | Same idea, but returns clean **structured** data (top processes by memory) |
| **Run** | One line — `mcp.run(...)` — to serve the tools |

The two tools:

| Tool | Parameters | Returns |
|------|-----------|---------|
| `run_command` | `command: str` (e.g. `"df -h"`) | Raw command output (text) |
| `list_top_processes` | `limit: int = 5` | A JSON list of `{user, pid, mem_percent, command}` |

---

## Prerequisites

- **Python 3.10+**
- The **`mcp` SDK** (v2+), installed below
- **Node.js** — only needed for the MCP Inspector (`npx`). Check with `node --version`.

---

## Setup

```bash
cd "Ep3 - Build and Host an MCP Server"

# (recommended) a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# install the official MCP SDK (with the CLI extras)
pip install "mcp[cli]"
```

Confirm you're on **v2+** (v1 used a different, older API):

```bash
pip show mcp | grep -i version      # expect 2.x or newer
```

> Add `.venv/` to your `.gitignore` so it doesn't get committed.

---

## Run the server

This server ships configured to run over **HTTP** (see the bottom of `server.py`):

```python
if __name__ == "__main__":
    # mcp.run()                                # stdio (local) — see "Transports" below
    mcp.run(transport="streamable-http")       # host it over HTTP
```

Start it:

```bash
python server.py
```

You should see a startup line like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

That means the server is live at **`http://127.0.0.1:8000/mcp`**. Leave it running.

> 🔎 **Don't open `http://127.0.0.1:8000/mcp` in your browser** — it's a machine-to-machine protocol endpoint, not a web page. A plain visit returns `400 Bad Request: Missing session ID`. That error actually means the server is working; you talk to it with an MCP **client** (the Inspector, below), not a browser.

---

## Verify it with the MCP Inspector (in your browser)

The **MCP Inspector** is a browser UI that acts as an MCP client, so you can browse and call your tools without writing any client code. Launch it with `npx` (needs Node):

### 1. Launch the Inspector

Open a **second terminal** (leave `python server.py` running in the first) and run:

```bash
npx @modelcontextprotocol/inspector
```

The first time, `npx` will ask to install the package — accept it. It prints something like:

```
🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=abc123...
```

**Open that exact URL** in your browser (the token matters — a bare `http://localhost:6274` may fail to connect).

### 2. Connect to *your* server

The Inspector ships with two bundled example servers — `filesystem-server-default` and `everything-server-default`. **Ignore those**; they aren't yours. To connect to your server, use the connection panel on the **left sidebar**:

1. **Transport Type** → select **`Streamable HTTP`**
2. **URL** → enter:
   ```
   http://127.0.0.1:8000/mcp
   ```
3. Click **Connect**. The status should turn green / "Connected."

### 3. Call the tools

1. Open the **Tools** tab and click **List Tools** — you should see **`run_command`** and **`list_top_processes`**, with parameter fields the SDK generated automatically.
2. Select **`run_command`**, set `command` = `df -h`, click **Run Tool** → you'll see the disk output.
3. Select **`list_top_processes`**, set `limit` = `5`, click **Run Tool** → a clean JSON table of the top memory users.
4. Try the guardrail: **`run_command`** with `command` = `rm -rf /` → **`REFUSED: 'rm' is not on the allowlist.`**

You'll also see each request logged in the terminal running `server.py`.

> **Alternative — stdio:** if you flip the file to `mcp.run()` (stdio) instead of HTTP, connect the Inspector with **Transport Type = STDIO**, **Command = `python`**, **Arguments = `server.py`** (use the Python where `mcp` is installed — your venv). There's also a shortcut, `mcp dev server.py`, that launches the Inspector for you — handy, but it depends on your local `mcp` CLI and can crash on some setups (e.g. an old `typer` in an Anaconda environment), so `npx` is the reliable path.

---

## Quick check without a browser (optional)

To confirm the file imports and both tools work — no Node, no Inspector:

```bash
python3 -c "
import asyncio, server
print('tools:', [t.name for t in asyncio.run(server.mcp.list_tools())])
print('df -h ->', server._safe_run('df -h')[:40])
print('rm    ->', server._safe_run('rm -rf /'))
"
```

Expected: `tools: ['run_command', 'list_top_processes']`, a real `df` line, and a `REFUSED: 'rm' ...`.

---

## Transports: stdio vs HTTP

MCP servers can talk over two transports — switch by editing the bottom of `server.py`:

- **stdio** (`mcp.run()`) — the client launches the server as a local subprocess and talks over stdin/stdout. Great for local dev; **no network port**. (If you run this and then try to curl port 8000, you'll get *connection refused* — that's expected, there's no HTTP server in stdio mode.)
- **streamable HTTP** (`mcp.run(transport="streamable-http")`) — the server listens on a network port (default `http://127.0.0.1:8000/mcp`), so a client on another machine can reach it. This is what the file ships with.

Change the host/port if you need to:

```python
mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
```

---

## Safety

The server only ever runs **read-only** diagnostics — the same guardrail from Episode 2, now living on the server where it protects *every* client:

- ✅ **Allowlist only:** `ls`, `cat`, `df`, `du`, `ps`, `grep`, and `kubectl get`. Everything else is refused.
- ✅ **No `shell=True`:** commands are parsed into an argument list, so there's no shell to inject into.
- ✅ **No chaining/pipes/redirects:** `; | & > < \` $(` are rejected (blocks tricks like `df -h; rm -rf /`).
- ✅ **Timeout:** no single command can hang the server.

Still, run it in a throwaway VM or container, and never point it at a production box or use production credentials. It's a learning tool.

---

## Troubleshooting

- **`curl: Connection refused` on port 8000** → the server isn't running in HTTP mode. Make sure `server.py` has the `mcp.run(transport="streamable-http")` line active and you see the `Uvicorn running...` log.
- **Browser shows `400 Missing session ID`** → expected. `/mcp` isn't browsable; use the Inspector.
- **`ModuleNotFoundError: No module named 'mcp.server.fastmcp'` / `FastMCP` errors** → you're on an old `mcp` version or following an old tutorial. v2 renamed the class to `MCPServer` (`from mcp.server import MCPServer`). Run `pip install -U "mcp[cli]"`.
- **`mcp dev` crashes with `Type not yet supported: str | None`** → your `mcp` CLI is running from an environment with an outdated `typer` (common with Anaconda). Use `npx @modelcontextprotocol/inspector` instead.
- **`npx: command not found`** → install Node.js (`brew install node` on macOS).
- **Inspector connects but no tools** → make sure `python server.py` is still running, and that you used Transport = Streamable HTTP with URL `http://127.0.0.1:8000/mcp`.

---

## What's next in the series

- **Ep 4 —** turn our Episode-2 agent into an **MCP client**: it connects to this server, discovers these tools on its own, and re-runs the investigation — against a server that can live on a *different* machine.

⭐ If this helped, star the repo and subscribe to the channel.
