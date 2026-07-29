#!/usr/bin/env python3
"""
A minimal AI agent — no framework, pure API calls.

This is deliberately ~120 lines so you can see the ENTIRE mechanism:
  1. a tool (an allowlisted, read-only shell runner)
  2. a loop that sends state to the model and dispatches tool calls
  3. that's it. That's an agent.

Run:
  export CLAUDE_KEY="sk-ant-..."   # off camera
  python3 agent.py "Which process is eating this box's memory?"
"""

import os
import sys
import json
import shlex
import subprocess

import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 10          # safety break: never loop forever (also caps token spend)
COMMAND_TIMEOUT = 30        # seconds; a command can't hang the agent

# ── The guardrail ────────────────────────────────────────────────────────────
# Read-only diagnostics ONLY. Anything not on this list is refused, not run.
ALLOWED = {"ls", "cat", "df", "du", "ps", "grep", "kubectl"}
# Characters that let one command smuggle in another (chaining, pipes, subshells,
# redirects). We reject them outright — this is the seed of the Security episode.
FORBIDDEN_CHARS = [";", "|", "&", ">", "<", "`", "$("]


def run_command(command: str) -> str:
    """Execute a shell command IF it passes the allowlist. Return its output."""
    for ch in FORBIDDEN_CHARS:
        if ch in command:
            return f"REFUSED: '{ch}' is not allowed (no chaining/pipes/redirects)."

    try:
        parts = shlex.split(command)
    except ValueError as e:
        return f"REFUSED: could not parse command ({e})."

    if not parts:
        return "REFUSED: empty command."

    base = parts[0]
    if base not in ALLOWED:
        return f"REFUSED: '{base}' is not on the allowlist {sorted(ALLOWED)}."
    if base == "kubectl" and (len(parts) < 2 or parts[1] != "get"):
        return "REFUSED: only 'kubectl get ...' is allowed."

    try:
        result = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"REFUSED: command timed out after {COMMAND_TIMEOUT}s."

    output = (result.stdout + result.stderr).strip()
    return output or "(no output)"


# ── The tool schema we advertise to the model ────────────────────────────────
TOOLS = [
    {
        "name": "run_command",
        "description": (
            "Run a READ-ONLY diagnostic shell command on the server and return its "
            "output. Allowed commands: ls, cat, df, du, ps, grep, and 'kubectl get'. "
            "Use this to investigate the system. Anything else will be refused."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The exact shell command to run, e.g. 'df -h'.",
                }
            },
            "required": ["command"],
        },
    }
]

SYSTEM_PROMPT = (
    "You are a DevOps diagnostic assistant. You investigate systems using the "
    "run_command tool, one command at a time, reasoning about each result before "
    "the next step. When you have found the answer, stop calling tools and give a "
    "short, clear final report of the root cause."
)


def call_claude(messages: list) -> dict:
    """One inference. Send the full state, get one response back."""
    resp = requests.post(
        API_URL,
        headers={
            "x-api-key": os.environ["CLAUDE_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "Which process is eating this box's memory?"

    # We (the client) hold the state. The model is stateless — Episode 1.
    messages = [{"role": "user", "content": task}]

    for i in range(1, MAX_ITERATIONS + 1):
        print(f"\n─── iteration {i} ───")
        response = call_claude(messages)

        # Print any text the model produced this turn (its reasoning / report).
        for block in response["content"]:
            if block["type"] == "text":
                print(block["text"])

        # If the model didn't ask for a tool, it's done.
        if response["stop_reason"] != "tool_use":
            print("\n✅ agent finished.")
            return

        # Record the model's turn verbatim (required for the next request).
        messages.append({"role": "assistant", "content": response["content"]})

        # Dispatch every tool the model asked for, collect the results.
        tool_results = []
        for block in response["content"]:
            if block["type"] != "tool_use":
                continue
            command = block["input"]["command"]
            print(f"🔧 run_command: {command}")
            output = run_command(command)
            print(output)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": output,
                }
            )

        # Hand the outputs back to the model as the next user turn.
        messages.append({"role": "user", "content": tool_results})

    print(f"\n⛔ hit MAX_ITERATIONS ({MAX_ITERATIONS}) — stopping.")


if __name__ == "__main__":
    main()
