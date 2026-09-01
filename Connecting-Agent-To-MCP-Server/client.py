#!/usr/bin/env python3
"""
Episode 4 — the agent, now as an MCP CLIENT.

It's the SAME loop as Episode 2. The only thing that changed: the tools aren't
hardcoded in this file anymore. We connect to the Episode-3 MCP server, ask it
what tools it has, and forward the model's tool calls to it over the protocol.
Because the server can live on another machine, the agent is no longer limited
to its own box.

Run:
  # 1. start the Episode-3 server over HTTP (in the Ep3 folder):
  #      python server.py       # serves http://127.0.0.1:8000/mcp
  # 2. then, here:
  export CLAUDE_KEY="sk-ant-..."
  python3 client.py "Which process is eating this box's memory?"
"""

import os
import sys
import asyncio

import requests
from mcp import Client

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 10
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"   # the Episode-3 server, over HTTP

SYSTEM_PROMPT = (
    "You are a DevOps diagnostic assistant. You investigate systems using the "
    "tools available to you, one call at a time, reasoning about each result "
    "before the next step. When you have found the answer, stop calling tools "
    "and give a short, clear final report of the root cause."
)


def call_claude(messages: list, tools: list) -> dict:
    """One inference. The same Anthropic call as Episode 2 — but the `tools`
    list is now whatever we discovered from the MCP server, not a hardcoded one."""
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
            "tools": tools,
            "messages": messages,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def result_to_text(result) -> str:
    """Flatten an MCP tool result into plain text to hand back to the model."""
    parts = [b.text for b in getattr(result, "content", []) if getattr(b, "text", None)]
    return "\n".join(parts) or "(no output)"


async def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "Which process is eating this box's memory?"

    # Connect to the MCP server (Episode 3), over HTTP.
    async with Client(MCP_SERVER_URL) as mcp:
        # 1. DISCOVER — ask the server what tools it has. We hardcode nothing.
        discovered = (await mcp.list_tools()).tools
        tools = [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for t in discovered
        ]
        print(f"🔌 connected to {MCP_SERVER_URL}")
        print(f"   discovered tools: {[t['name'] for t in tools]}\n")

        # We (the client) still carry the conversation state — Episode 1.
        messages = [{"role": "user", "content": task}]

        for i in range(1, MAX_ITERATIONS + 1):
            print(f"─── iteration {i} ───")
            response = call_claude(messages, tools)

            for block in response["content"]:
                if block["type"] == "text":
                    print(block["text"])

            if response["stop_reason"] != "tool_use":
                print("\n✅ agent finished.")
                return

            messages.append({"role": "assistant", "content": response["content"]})

            tool_results = []
            for block in response["content"]:
                if block["type"] != "tool_use":
                    continue
                print(f"🔧 calling MCP tool: {block['name']}  args={block['input']}")
                # 2. DISPATCH — forward the model's call to the server over the protocol.
                result = await mcp.call_tool(block["name"], block["input"])
                output = result_to_text(result)
                print(output)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": output,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        print(f"\n⛔ hit MAX_ITERATIONS ({MAX_ITERATIONS}) — stopping.")


if __name__ == "__main__":
    asyncio.run(main())
