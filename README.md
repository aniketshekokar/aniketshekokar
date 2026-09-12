# Megatron

Megatron is a browser-based, Jarvis-style personal assistant. It has a voice-ready command surface, speech replies, a command transcript, and a dependency-free local assistant engine that can store tasks and notes, tell the date/time, and launch web searches.

## Run locally

This project intentionally has no build step or package installation. Start the assistant engine and static UI together:

```bash
python3 server.py
```

Then open [http://localhost:8000](http://localhost:8000). Voice input uses the browser's Web Speech API when available. Local tasks and notes are stored in `data/megatron.json`, which is intentionally excluded from Git.

## Included interactions

- Send a typed request using **Enter** or the arrow button, then read the response in the command log.
- Select the voice icon to dictate a request; Megatron can also speak answers (use the Voice replies toggle to disable this).
- Use `add task Buy sensors`, `list tasks`, and `complete task 1` to manage a task list.
- Use `note Project idea` and `list notes` to save and retrieve notes locally.
- Use `search for weather in Pune` to open a web search in a new browser tab.
- Ask `help`, `time`, or `date` for built-in assistant commands.
