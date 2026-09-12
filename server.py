"""Megatron's dependency-free local assistant server."""

from __future__ import annotations

import json
import re
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "megatron.json"


def load_memory() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"tasks": [], "notes": []}


def save_memory(memory: dict) -> None:
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")


def respond(message: str) -> dict:
    """Process deterministic Jarvis-style commands without an external API key."""
    text = message.strip()
    command = text.lower()
    memory = load_memory()

    if command in {"help", "what can you do", "commands"}:
        return {"reply": "I can manage local tasks and notes, report the date or time, and open a web search. Say: add task ..., list tasks, complete task 1, note ..., list notes, or search for ..."}
    if "time" in command:
        return {"reply": f"The current time is {datetime.now():%I:%M %p}."}
    if command in {"date", "what is the date", "today"} or "what's the date" in command:
        return {"reply": f"Today is {datetime.now():%A, %B %-d, %Y}."}

    task = re.match(r"(?:add )?task\s*[:\-]?\s*(.+)", text, re.I)
    if task:
        memory["tasks"].append({"title": task.group(1), "done": False})
        save_memory(memory)
        return {"reply": f"Task added: {task.group(1)}."}
    if command in {"list tasks", "show tasks", "my tasks"}:
        active = [f"{index + 1}. {item['title']}" for index, item in enumerate(memory["tasks"]) if not item["done"]]
        return {"reply": "Your active tasks: " + ("; ".join(active) if active else "none yet.")}
    done = re.match(r"(?:complete|finish|done) task\s+(\d+)", command)
    if done:
        index = int(done.group(1)) - 1
        if 0 <= index < len(memory["tasks"]):
            memory["tasks"][index]["done"] = True
            save_memory(memory)
            return {"reply": f"Completed: {memory['tasks'][index]['title']}."}
        return {"reply": "I could not find that task number. Ask me to list tasks first."}

    note = re.match(r"(?:save )?note\s*[:\-]?\s*(.+)", text, re.I)
    if note:
        memory["notes"].append(note.group(1))
        save_memory(memory)
        return {"reply": "Note saved locally."}
    if command in {"list notes", "show notes", "my notes"}:
        notes = memory["notes"]
        return {"reply": "Your notes: " + ("; ".join(notes) if notes else "none yet.")}

    search = re.match(r"(?:search(?: for)?|google)\s+(.+)", text, re.I)
    if search:
        query = search.group(1)
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        return {"reply": f"Opening a web search for {query}.", "action": {"url": url}}
    return {"reply": "I am ready. Say “help” to see my local assistant commands, or ask me to search for something."}


class MegatronHandler(SimpleHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/api/assistant":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length))
            result = respond(payload["message"])
        except (json.JSONDecodeError, KeyError, TypeError):
            self.send_error(HTTPStatus.BAD_REQUEST, "A message is required")
            return
        body = json.dumps(result).encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Megatron is online at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), MegatronHandler).serve_forever()
