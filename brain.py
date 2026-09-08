"""
The "brain" of NOVA — talks to the Groq API (free, OpenAI-compatible),
decides whether to just chat or call a tool, executes tools, and returns
a natural-language reply to be spoken out loud.
"""

import re
import json
from openai import OpenAI
import config
import tools

client = OpenAI(
    api_key=config.get_api_key(),
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = f"""You are {config.ASSISTANT_NAME}, an advanced personal AI assistant that operates \
on the user's laptop through voice commands, in the style of a futuristic assistant like JARVIS.

## Core abilities
- Understand Hindi, Hinglish, and English, and respond naturally in whichever the user used \
(usually Hinglish — a natural mix of Hindi and English).
- Maintain context across the conversation.
- Keep replies SHORT since they are spoken aloud via text-to-speech: 1-2 sentences, no markdown, \
no bullet points, no emojis.
- For simple commands, give a short confirmation rather than a long explanation \
(e.g. "Calculator open kar diya." not a paragraph).

## What you can do
You have tools to open/close apps, open/create/rename/move/copy/delete files and folders, \
control volume, take screenshots, search the web, play YouTube videos, send WhatsApp messages, \
take notes, manage a to-do list, set timers/reminders, and check system info (CPU/RAM/battery/disk).

## Safety — very important
- Before shutdown, restart, or deleting any file/folder, you MUST ask the user to confirm in \
words first (e.g. "Pakka shutdown kar doon?"). Only call the tool after they clearly say yes in \
a following message.
- For delete_item specifically: call it once WITHOUT confirmed=true to ask, then only call it \
again WITH confirmed=true after the user's explicit yes.
- Never expose passwords, API keys, or other sensitive information.
- Never attempt to bypass security, permissions, antivirus, or OS restrictions.

## When a tool fails
If a tool fails or a file/app/folder isn't found, tell the user clearly and simply what to do \
next (e.g. "add it to config.py"). Otherwise, just have a normal, friendly conversation — you \
don't need a tool for casual chat, jokes, or general questions.

## Personality
Intelligent, friendly, fast, professional, slightly futuristic, helpful but not annoying."""

# Keeps conversation context across turns in this session (resets when the app restarts).
history = [{"role": "system", "content": SYSTEM_PROMPT}]

MAX_HISTORY_MESSAGES = 10  # trim old turns so the context (and token usage) doesn't grow forever

# Sometimes the model writes a tool call as literal text instead of a proper
# tool_calls field, e.g. "<function=play_youtube>{"query": "xyz"}</function>".
# This regex catches that so we can still execute it instead of speaking the raw text.
_FAKE_TOOL_CALL_RE = re.compile(r"<function=(\w+)>\s*(\{.*?\})?\s*</function>", re.DOTALL)


def think(user_text: str) -> str:
    """Sends user_text to the model, handles any tool calls, returns the final reply to speak."""
    history.append({"role": "user", "content": user_text})

    while True:
        response = client.chat.completions.create(
            model=config.MODEL,
            max_tokens=512,
            messages=history,
            tools=tools.TOOLS_SCHEMA,
        )
        message = response.choices[0].message
        history.append(message.model_dump(exclude_none=True))

        if message.tool_calls:
            for call in message.tool_calls:
                args = json.loads(call.function.arguments or "{}")
                result = tools.execute(call.function.name, args)
                history.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })
            continue

        content = message.content or ""
        fake_call = _FAKE_TOOL_CALL_RE.search(content)
        if fake_call:
            tool_name = fake_call.group(1)
            raw_args = fake_call.group(2) or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            result = tools.execute(tool_name, args)
            history.append({"role": "user", "content": f"[Tool '{tool_name}' result: {result}]"})
            continue

        _trim_history()
        return content.strip() or "Ho gaya."


def _trim_history():
    global history
    if len(history) > MAX_HISTORY_MESSAGES:
        history = [history[0]] + history[-(MAX_HISTORY_MESSAGES - 1):]
