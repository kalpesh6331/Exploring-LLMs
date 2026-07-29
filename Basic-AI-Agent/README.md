# Build an AI Agent from Scratch (No Framework)

A tiny, fully transparent **AI agent in ~120 lines of Python** — no framework, no SDK magic, just plain API calls so you can see *the entire mechanism*.

This is the companion code for **Episode 2** of the **DevOps & Data Simplified — AI** series. The agent investigates a real ops problem on its own:

> **"Which process is eating this box's memory?"**

It runs read-only diagnostic commands, reasons about the output, decides the next step, and reports the root cause — the same way an on-call engineer would.

📺 *Watch the walkthrough:* `<add your YouTube link here>`

---

## The one idea

An "AI agent" isn't magic. It's a **`while` loop** around a stateless model that can call **your** tools:

```
send the task ─▶ model asks to run a tool ─▶ you run it ─▶ feed the output back ─▶ (loop)
                                                                    │
                                          model gives a final answer ─▶ done
```

The model never touches your system. It can only *ask*. Your code decides what actually runs. **The model proposes; your code disposes.**

---

## What's inside `agent.py`

| Block | What it does |
|-------|--------------|
| **Setup** | Imports + knobs (`MODEL`, `MAX_ITERATIONS`, `COMMAND_TIMEOUT`) |
| **The tool** | `run_command()` — an **allowlisted, read-only** shell runner |
| **The schema** | `TOOLS` — how we tell the model the tool exists |
| **The system prompt** | The agent's job description (role · method · stop condition) |
| **The API call** | `call_claude()` — one stateless inference |
| **The loop** | `main()` — call → read → dispatch → append, capped by `MAX_ITERATIONS` |

---

## Prerequisites

- **Python 3.8+**
- The **`requests`** library (the only dependency)
- An **Anthropic API key** (from the developer console — this is *separate* from a Claude.ai subscription)

---

## Get an API key

1. Go to **[console.anthropic.com](https://console.anthropic.com)** and sign up. > ⚠️ The developer console is **not** the same as a Claude Pro/Team subscription — the API is billed separately, per token.
2. **Set up billing first** (Settings → Billing). This is the #1 reason a brand-new key returns errors: the key exists, but requests are rejected until the account can be billed.
3. Create the key (Settings → API Keys → **Create Key**) and **copy it immediately** — it's shown only once and starts with `sk-ant-`.

---

## Setup

```bash
# 1. install the one dependency
pip install requests

# 2. set your key as an environment variable (never hard-code it)
export CLAUDE_KEY="sk-ant-..."
```

> The agent reads the key from the `CLAUDE_KEY` environment variable. Keep it out of your code and out of version control.

---

## Run it

```bash
# default question ("Which process is eating this box's memory?")
python3 agent.py

# or ask your own
python3 agent.py "Which process is eating this box's memory?"
python3 agent.py "How much disk is free, and what's using the most space in /var?"
```

You'll see each loop iteration print the command the model chose, its output, and finally the agent's conclusion:

```
─── iteration 1 ───
🔧 run_command: ps aux
USER   PID  %CPU %MEM ...
─── iteration 2 ───
✅ agent finished.
The process using the most memory is ... (PID ...), holding ~NN% of RAM.
```

---

## Safety: this runs real commands

The agent executes shell commands **on the machine you run it on**. It's locked down, but treat it accordingly:

- ✅ **Allowlist (read-only only):** `ls`, `cat`, `df`, `du`, `ps`, `grep`, and `kubectl get`. Anything else is **refused, not run**.
- ✅ **No shell injection:** commands are parsed into an argument list (`shlex`) and run without `shell=True`.
- ✅ **No chaining/pipes/redirects:** the characters `; | & > < \` $(` are rejected, so a safe command can't smuggle in a dangerous one (e.g. `df -h; rm -rf /`).
- ✅ **Timeout:** no single command can hang the agent (`COMMAND_TIMEOUT`).

Even so, for peace of mind, **run it in a throwaway VM or container**, and **never point it at a production machine or use production credentials.** It's a learning tool.

Try the guardrail yourself — ask it to do something destructive and watch it get blocked:

```bash
python3 agent.py "Find the process eating the memory and kill it."
# → REFUSED: 'kill' is not on the allowlist
```

---

## Tweak it

Open `agent.py` and change the knobs at the top:

| Constant | Default | What it controls |
|----------|---------|------------------|
| `MODEL` | `claude-sonnet-4-6` | Which model to call (try a smaller/faster one) |
| `MAX_ITERATIONS` | `10` | The loop's leash — max turns before it stops |
| `COMMAND_TIMEOUT` | `30` | Seconds any single command may run |
| `ALLOWED` | `ls, cat, df, du, ps, grep, kubectl` | The read-only command allowlist |

Want it to diagnose something else? Add a safe command to `ALLOWED` and give it a new task.

---

## Troubleshooting

- **`KeyError: 'CLAUDE_KEY'`** → you didn't export the key in this shell. Run `export CLAUDE_KEY="sk-ant-..."` again.
- **401 / authentication error** → the key is wrong or revoked. Create a new one.
- **400 / billing or credit error** → set up billing in the console; a key with no billing can't make requests.
- **A command comes back `REFUSED`** → that's the allowlist working as designed. Add the command to `ALLOWED` if it's safe and read-only.
- **Model / version errors** → model names and the `anthropic-version` header change over time. Confirm the current values in the [Anthropic docs](https://docs.anthropic.com) if a call is rejected.
