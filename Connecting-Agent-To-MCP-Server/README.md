# Connect an Agent to an MCP Server

The Episode-2 AI agent, now rebuilt as an **MCP client**. It connects to the Episode-3 MCP server over HTTP, **discovers** the tools the server offers, and **forwards** the model's tool calls to it over the protocol — so the agent can use tools it doesn't contain, running on a machine it isn't on.

This is the companion code for **Episode 4** of the **DevOps & Data Simplified — AI** series.

---

## The one idea

`client.py` is Episode 2's `agent.py` with **two changes**:

1. **Discover** — instead of a hardcoded `TOOLS` list, the agent asks the server what tools it has (`tools/list`) at runtime.
2. **Dispatch** — instead of calling a local `run_command(...)`, the agent forwards the model's tool call to the server (`tools/call`) and hands the result back.

Everything else — the loop, the message history, `tool_use` / `tool_result`, the max-iterations leash — is Episode 2, unchanged.

> **The loop is the same — the tools just moved to the network.**

---

## What's inside `client.py`

| Section | What it does |
|---------|--------------|
| **Setup** | Constants + `MCP_SERVER_URL` (the Ep-3 server, over HTTP). Note what's *gone*: no allowlist, no `run_command`, no hand-written schema — that all lives on the server now. |
| **`call_claude`** | One Anthropic inference. Same as Episode 2 — except `tools` is now a parameter (we don't know the tools until we've asked the server). |
| **`result_to_text`** | Flattens an MCP tool result into plain text for the model. |
| **`main` → discover** | Connects to the server, calls `list_tools()`, and reshapes each tool into `{name, description, input_schema}` — the MCP schema passes straight through to Anthropic. |
| **`main` → the loop** | The Episode-2 loop, with one line changed: `await mcp.call_tool(...)` instead of the local function. |

---

## Prerequisites

- **Python 3.10+**
- The **`mcp` SDK** (v2+) and **`requests`**, installed below
- An **Anthropic API key** (from [console.anthropic.com](https://console.anthropic.com) — separate from a Claude.ai subscription; set up billing first)
- **The Episode-3 MCP server**, running over HTTP (see below)

---

## Setup

```bash
cd "Connecting-Agent-To-MCP-Server"

# (recommended) a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# the client needs both the MCP SDK and requests
pip install "mcp[cli]" requests

# your API key (never hard-code it)
export CLAUDE_KEY="sk-ant-..."
```

> Confirm you're on the current SDK: `pip show mcp | grep -i version` (tested against **v2.1.1**). Add `.venv/` to your `.gitignore`.

---

## Run it (two terminals)

The tool lives on the server now, so you need **both** running.

**Terminal 1 — start the Episode-3 server (HTTP):**
```bash
cd "../Building-MCP-Server"
python server.py            # serves http://127.0.0.1:8000/mcp
```
Wait for `Uvicorn running on http://127.0.0.1:8000`. Leave it running.

**Terminal 2 — run the agent (now a client):**
```bash
python3 client.py "Which process is eating this box's memory?"
```

You'll see it connect, **print the tools it discovered**, then investigate — likely reaching for `list_top_processes`, a tool that isn't in this file at all:

```
🔌 connected to http://127.0.0.1:8000/mcp
   discovered tools: ['run_command', 'list_top_processes']

─── iteration 1 ───
🔧 calling MCP tool: list_top_processes  args={'limit': 5}
[ ...structured JSON of the top memory users... ]
─── iteration 2 ───
✅ agent finished.
The process using the most memory is ... (PID ...).
```

Watch **Terminal 1** too — you'll see the tool calls arrive at the server. Two programs, talking.

> 💡 To make the demo interesting, give it something to find: start a memory hog first, e.g. `stress-ng --vm 1 --vm-bytes 1G` (or a small Python script that allocates a few hundred MB and sleeps).

---

## Point it at a server on another machine

This is the whole payoff. The agent isn't limited to its own box — change **one line** at the top of `client.py`:

```python
MCP_SERVER_URL = "http://<other-host-or-container>:8000/mcp"
```

Same agent, same loop — now diagnosing a **different** machine. (For the server to be reachable from another box, start it bound to all interfaces: `mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)` in the Ep-3 `server.py`.)

---

## Safety

The client is deliberately "dumb" — it just forwards whatever tool the model asks for. **All the safety lives on the server** (the Episode-3 allowlist: read-only commands only, no shell injection, no chaining, timeouts). That's the point: write the guardrail once, on the server, and *every* client that connects is protected by it — no matter who wrote the client. Try it:

```bash
python3 client.py "Find the process eating the memory and kill it."
# the model reaches for `kill`; the SERVER refuses it — the client never even could
```

Run the server in a throwaway VM or container, and never point it at a production box or use production credentials. It's a learning tool.

---

## How it works (the two new pieces)

**Discover** — ask the server for its tools and adapt them to the model's format:
```python
discovered = (await mcp.list_tools()).tools
tools = [
    {"name": t.name, "description": t.description, "input_schema": t.input_schema}
    for t in discovered
]
```
The MCP tool already carries its own JSON schema, so `input_schema` is a straight pass-through to Anthropic's `tools` field — no hand-written schema.

**Dispatch** — forward the model's tool call to the server:
```python
result = await mcp.call_tool(block["name"], block["input"])
```
This line doesn't care *which* tool the model picked. Add a new tool to the server tomorrow, and this same agent can use it — no code change here.

---

## Troubleshooting

- **`httpx.ConnectError` / connection refused** → the Episode-3 server isn't running (or not in HTTP mode). Start it first and confirm the `Uvicorn running...` log.
- **`KeyError: 'CLAUDE_KEY'`** → export your API key in this shell: `export CLAUDE_KEY="sk-ant-..."`.
- **401 / 400 from the API** → bad/revoked key, or billing/credits not set up in the console.
- **`ModuleNotFoundError: No module named 'requests'` (or `mcp`)** → install both in the *same* venv: `pip install "mcp[cli]" requests`.
- **`input_schema` is `None` / tool schema looks empty** → SDK version drift. This code targets `mcp` **v2.x**, where the attribute is `input_schema` (snake_case). Check `pip show mcp`.
- **Discovers 0 tools** → you're pointed at the wrong URL, or the server exposes no tools. Confirm `MCP_SERVER_URL` matches the server's address (`http://127.0.0.1:8000/mcp`).

---

## What's next in the series

- **Ep 5 —** we give this agent real *knowledge* with RAG, so it can answer questions about your own systems, runbooks, and docs — not just what it can poke at with a command.

⭐ If this helped, star the repo and subscribe to the channel.
