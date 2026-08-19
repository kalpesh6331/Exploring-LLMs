#!/usr/bin/env python3
"""
A minimal MCP server — it exposes our Episode-2 diagnostic tools over a
standard protocol, so ANY agent can discover and use them.

We write plain Python functions and add one decorator. The MCP SDK turns them
into a discoverable server — no protocol code by hand.

Two tools:
  1. run_command       — the allowlisted, read-only shell runner (lifted from Ep 2)
  2. list_top_processes — the same idea, but returns clean, structured data

Run it:
  pip install "mcp[cli]"
  mcp dev server.py                      # local (stdio) + opens the MCP Inspector
  python3 server.py                      # host it over HTTP (see the bottom of the file)
"""

import shlex
import subprocess

from mcp.server import MCPServer

# The server. The name is what a client sees when it connects.
mcp = MCPServer("devops-diagnostics")


# ── The guardrail: the exact safety rules from Episode 2 ─────────────────────
ALLOWED = {"ls", "cat", "df", "du", "ps", "grep", "kubectl"}
FORBIDDEN_CHARS = [";", "|", "&", ">", "<", "`", "$("]
COMMAND_TIMEOUT = 30  # seconds; a command can't hang the server


def _safe_run(command: str) -> str:
    """Run a shell command ONLY if it passes the allowlist; otherwise refuse it.

    This is the same safety logic we wrote in Ep 2 — it just lives on the
    server now, where it belongs.
    """
    # 1. No shell tricks: reject chaining, pipes, redirects, subshells.
    for ch in FORBIDDEN_CHARS:
        if ch in command:
            return f"REFUSED: '{ch}' is not allowed (no chaining/pipes/redirects)."

    # 2. Split "df -h" into ["df", "-h"] so there is no shell to inject into.
    parts = shlex.split(command)
    if not parts:
        return "REFUSED: empty command."

    # 3. Only allow the read-only commands on our list.
    base = parts[0]
    if base not in ALLOWED:
        return f"REFUSED: '{base}' is not on the allowlist {sorted(ALLOWED)}."
    if base == "kubectl" and (len(parts) < 2 or parts[1] != "get"):
        return "REFUSED: only 'kubectl get ...' is allowed."

    # 4. Run it, with a timeout so it can never hang the server.
    try:
        result = subprocess.run(
            parts, capture_output=True, text=True, timeout=COMMAND_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return f"REFUSED: command timed out after {COMMAND_TIMEOUT}s."

    return (result.stdout + result.stderr).strip() or "(no output)"


# ── Tool 1: the raw diagnostic runner (lifted from Episode 2) ────────────────
@mcp.tool()
def run_command(command: str) -> str:
    """Run a READ-ONLY diagnostic shell command and return its output.

    Allowed commands: ls, cat, df, du, ps, grep, and 'kubectl get'.
    Anything else is refused.
    """
    return _safe_run(command)


# ── Tool 2: the same data, but structured ────────────────────────────────────
@mcp.tool()
def list_top_processes(limit: int = 5) -> list[dict]:
    """List the processes using the most memory, as clean structured rows.

    limit: how many processes to return (default 5).
    """
    output = _safe_run("ps aux")

    processes = []
    for line in output.splitlines()[1:]:      # skip the header row
        columns = line.split(None, 10)        # split into at most 11 columns
        if len(columns) < 11:
            continue
        processes.append(
            {
                "user": columns[0],
                "pid": columns[1],
                "mem_percent": float(columns[3]),
                "command": columns[10],
            }
        )

    # Biggest memory user first, then keep only the top `limit`.
    processes.sort(key=lambda p: p["mem_percent"], reverse=True)
    return processes[:limit]


# ── Run the server ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # mcp.run()                                # stdio (local) — the default
    mcp.run(transport="streamable-http")       # host it over HTTP
