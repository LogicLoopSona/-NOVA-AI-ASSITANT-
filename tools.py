"""
Tools that NOVA (the LLM) can call to actually DO things on this laptop.

Each tool function takes keyword args (matching its schema) and returns a
short STRING result — the AI reads that result and decides what to say back
to the user in natural language.

To add a new tool:
  1. Write a function here that returns a string.
  2. Add its schema via _tool(...) in TOOLS_SCHEMA.
  3. Add an entry in the TOOL_FUNCTIONS dict at the bottom.
"""

import os
import re
import shutil
import subprocess
import threading
import webbrowser
import datetime
import platform

import config


# ---------- App / system control ----------

def _resolve_app_path(path: str):
    if path.startswith("start "):
        return path
    found = shutil.which(path)
    if found:
        return found
    for candidate in config.COMMON_INSTALL_PATHS.get(path.lower(), []):
        expanded = os.path.expandvars(candidate)
        if os.path.exists(expanded):
            return expanded
    return None


def _find_start_menu_shortcut(query: str):
    query = query.lower().strip()
    if not query:
        return None
    for raw_dir in config.START_MENU_SEARCH_DIRS:
        d = os.path.expandvars(raw_dir)
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(".lnk") and query in f.lower():
                    return os.path.join(root, f)
    return None


def open_app(app_name: str) -> str:
    """Opens any installed app by name."""
    query = app_name.lower().strip()

    for name, path in config.APP_PATHS.items():
        if name in query or query in name:
            if path.startswith("start "):
                os.system(path)
                return f"Opened {name}."
            resolved = _resolve_app_path(path)
            if resolved:
                try:
                    subprocess.Popen([resolved])
                    return f"Opened {name}."
                except Exception as e:
                    return f"Found {name} but failed to launch it: {e}"
            return f"Couldn't find {name} installed at the expected location. Ask the user for its install path so it can be added to config.py."

    shortcut = _find_start_menu_shortcut(query)
    if shortcut:
        try:
            os.startfile(shortcut)
            return f"Opened {app_name} via Start Menu shortcut."
        except Exception as e:
            return f"Found a shortcut for {app_name} but failed to open it: {e}"

    result = os.system(f'start "" "{app_name}"')
    if result == 0:
        return f"Attempted to open {app_name} via Windows 'start'. It should be opening now."
    return f"Could not find any app called '{app_name}' on this laptop. Tell the user it needs to be added to config.py APP_PATHS with the correct path."


def close_app(app_name: str) -> str:
    """Force-closes an app by name."""
    query = app_name.lower().strip()
    matched = None
    for name, path in config.APP_PATHS.items():
        if name in query:
            matched = path
            break
    exe = os.path.basename(matched).replace("start ", "") if matched else query.split()[0] + ".exe"
    try:
        subprocess.run(["taskkill", "/F", "/IM", exe], shell=True, capture_output=True)
        return f"Closed {app_name}."
    except Exception as e:
        return f"Failed to close {app_name}: {e}"


def system_control(action: str) -> str:
    """action: one of 'shutdown', 'restart', 'lock', 'cancel_shutdown'"""
    action = action.lower().strip()
    if action == "shutdown":
        os.system("shutdown /s /t 10")
        return "Shutting down in 10 seconds. User can say cancel to stop it."
    if action == "restart":
        os.system("shutdown /r /t 10")
        return "Restarting in 10 seconds."
    if action == "lock":
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locked the PC."
    if action == "cancel_shutdown":
        os.system("shutdown /a")
        return "Cancelled the pending shutdown/restart."
    return f"Unknown system action: {action}"


# ---------- Volume control ----------

def control_volume(action: str) -> str:
    """action: 'up', 'down', 'mute', 'unmute'"""
    try:
        import pyautogui
    except ImportError:
        return "pyautogui isn't installed. Tell the user to run: pip install pyautogui"

    action = action.lower().strip()
    if action == "up":
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Volume increased."
    if action == "down":
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Volume decreased."
    if action in ("mute", "unmute"):
        pyautogui.press("volumemute")
        return f"Toggled mute ({action})."
    return f"Unknown volume action: {action}"


# ---------- Web ----------

def web_search(query: str) -> str:
    """Opens a Google search for the query in the default browser."""
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Opened a Google search for '{query}' in the browser."


def open_website(url: str) -> str:
    """Opens a website. Checks config.WEBSITES for a saved shortcut by name first,
    then falls back to treating the input as a raw URL/domain."""
    query = url.lower().strip()

    for name, full_url in config.WEBSITES.items():
        if name in query or query in name:
            webbrowser.open(full_url)
            return f"Opened {name}."

    if not url.startswith("http"):
        url = "https://" + url.replace(" ", "")
    webbrowser.open(url)
    return f"Opened {url} in the browser."


def play_youtube(query: str) -> str:
    """Directly plays the top YouTube result for the query."""
    try:
        import pywhatkit
        pywhatkit.playonyt(query)
        return f"Now playing '{query}' on YouTube."
    except ImportError:
        return "pywhatkit isn't installed, can't play YouTube directly. Tell the user to run: pip install pywhatkit"
    except Exception as e:
        return f"Failed to play '{query}': {e}"


# ---------- Folders & files ----------

def _search_common_folders(query: str, max_depth: int = 2):
    query = query.lower().strip()
    home = os.path.expanduser("~")
    search_roots = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "OneDrive", "Desktop"),
        os.path.join(home, "OneDrive", "Documents"),
    ]
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        base_depth = root.rstrip(os.sep).count(os.sep)
        for current_root, dirs, _ in os.walk(root):
            depth = current_root.rstrip(os.sep).count(os.sep) - base_depth
            if depth >= max_depth:
                dirs[:] = []
                continue
            for d in dirs:
                if query in d.lower():
                    return os.path.join(current_root, d)
    return None


def open_folder(folder_name: str) -> str:
    query = folder_name.lower().strip()

    for name, path in config.FOLDER_PATHS.items():
        if name.lower() in query or query in name.lower():
            if os.path.isdir(path):
                os.startfile(path)
                return f"Opened the {name} folder."
            return f"The configured path for {name} doesn't exist anymore. Ask the user to check config.py FOLDER_PATHS."

    found = _search_common_folders(query)
    if found:
        os.startfile(found)
        return f"Found and opened folder '{folder_name}' at {found}."

    return f"Couldn't find a folder called '{folder_name}' in Desktop, Documents, or Downloads. Ask the user for its exact path so it can be added to config.py FOLDER_PATHS."


def _resolve_item_path(name_or_path: str):
    """If given a full path, use it. Otherwise search common folders for a matching name."""
    if os.path.exists(name_or_path):
        return name_or_path
    return _search_common_folders(name_or_path, max_depth=3)


def create_folder(folder_name: str, location: str = "desktop") -> str:
    """Creates a new folder. location can be a configured folder name or a full path (default: Desktop)."""
    base = config.FOLDER_PATHS.get(location.lower(), os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"))
    if not os.path.isdir(base):
        base = os.path.join(os.path.expanduser("~"), "Desktop")
    new_path = os.path.join(base, folder_name)
    try:
        os.makedirs(new_path, exist_ok=True)
        return f"Created folder '{folder_name}' at {new_path}."
    except Exception as e:
        return f"Failed to create folder: {e}"


def rename_item(current_name: str, new_name: str) -> str:
    """Renames a file or folder found by name."""
    path = _resolve_item_path(current_name)
    if not path:
        return f"Couldn't find '{current_name}' to rename. Ask the user for its exact path."
    new_path = os.path.join(os.path.dirname(path), new_name)
    try:
        os.rename(path, new_path)
        return f"Renamed '{current_name}' to '{new_name}'."
    except Exception as e:
        return f"Failed to rename: {e}"


def move_item(item_name: str, destination: str) -> str:
    """Moves a file or folder to a destination (config folder name or full path)."""
    path = _resolve_item_path(item_name)
    if not path:
        return f"Couldn't find '{item_name}' to move. Ask the user for its exact path."
    dest = config.FOLDER_PATHS.get(destination.lower(), destination)
    if not os.path.isdir(dest):
        return f"Destination '{destination}' doesn't exist. Ask the user to confirm the path or add it to config.py FOLDER_PATHS."
    try:
        shutil.move(path, dest)
        return f"Moved '{item_name}' to {dest}."
    except Exception as e:
        return f"Failed to move: {e}"


def copy_item(item_name: str, destination: str) -> str:
    """Copies a file or folder to a destination (config folder name or full path)."""
    path = _resolve_item_path(item_name)
    if not path:
        return f"Couldn't find '{item_name}' to copy. Ask the user for its exact path."
    dest = config.FOLDER_PATHS.get(destination.lower(), destination)
    if not os.path.isdir(dest):
        return f"Destination '{destination}' doesn't exist. Ask the user to confirm the path or add it to config.py FOLDER_PATHS."
    try:
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(dest, os.path.basename(path)))
        else:
            shutil.copy2(path, dest)
        return f"Copied '{item_name}' to {dest}."
    except Exception as e:
        return f"Failed to copy: {e}"


def delete_item(item_name: str, confirmed: bool = False) -> str:
    """
    Deletes a file or folder. ONLY call with confirmed=True after the user has
    explicitly confirmed in a previous message that they want it deleted.
    """
    if not confirmed:
        return "NOT deleted — confirmation required. Ask the user to explicitly confirm before calling this again with confirmed=true."
    path = _resolve_item_path(item_name)
    if not path:
        return f"Couldn't find '{item_name}' to delete."
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return f"Deleted '{item_name}'."
    except Exception as e:
        return f"Failed to delete: {e}"


# ---------- Screenshot ----------

def take_screenshot(_: str = "") -> str:
    try:
        import pyautogui
    except ImportError:
        return "pyautogui isn't installed. Tell the user to run: pip install pyautogui"

    os.makedirs(config.SCREENSHOTS_FOLDER, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(config.SCREENSHOTS_FOLDER, f"screenshot_{timestamp}.png")
    try:
        img = pyautogui.screenshot()
        img.save(filepath)
        return f"Screenshot saved to {filepath}."
    except Exception as e:
        return f"Failed to take screenshot: {e}"


# ---------- Document reading (Word, PowerPoint, PDF, text files) ----------

def _find_document(query: str):
    """Searches common folders + configured folders for a file matching query."""
    query = query.lower().strip()
    home = os.path.expanduser("~")
    search_roots = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "OneDrive", "Desktop"),
        os.path.join(home, "OneDrive", "Documents"),
    ] + list(config.FOLDER_PATHS.values())

    doc_extensions = (".docx", ".pptx", ".pdf", ".txt")
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for current_root, dirs, files in os.walk(root):
            # Don't descend too deep
            depth = current_root[len(root):].count(os.sep)
            if depth >= 3:
                dirs[:] = []
                continue
            for f in files:
                if query in f.lower() and f.lower().endswith(doc_extensions):
                    return os.path.join(current_root, f)
    return None


def read_document(file_name: str) -> str:
    """Reads a .docx, .pptx, .pdf, or .txt file by name and returns its text content."""
    path = _find_document(file_name)
    if not path:
        return f"Couldn't find a document called '{file_name}' in common folders. Ask the user for its exact path."

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".docx":
            import docx
            doc = docx.Document(path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        elif ext == ".pptx":
            from pptx import Presentation
            prs = Presentation(path)
            parts = []
            for i, slide in enumerate(prs.slides, 1):
                slide_text = [f"Slide {i}:"]
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text)
                parts.append("\n".join(slide_text))
            text = "\n\n".join(parts)
        elif ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            return f"Unsupported file type: {ext}"
    except ImportError as e:
        return f"Missing library to read {ext} files: {e}. Tell the user to run: pip install python-docx python-pptx pypdf"
    except Exception as e:
        return f"Failed to read '{file_name}': {e}"

    if not text.strip():
        return f"Opened '{file_name}' but it appears to be empty or the text couldn't be extracted."

    truncated = text[:3000]
    note = " (truncated, file is longer)" if len(text) > 3000 else ""
    return f"Content of '{file_name}'{note}:\n{truncated}"


# ---------- Coding: write and run code ----------

CODE_FOLDER = "code"

_EXT_BY_LANGUAGE = {
    "python": ".py",
    "javascript": ".js",
    "html": ".html",
    "css": ".css",
    "c": ".c",
    "cpp": ".cpp",
    "java": ".java",
}

_RUN_CMD_BY_EXT = {
    ".py": ["python"],
    ".js": ["node"],
}


def write_code(filename: str, code: str, language: str = "python") -> str:
    """Writes code to a file in the local 'code' folder. Adds the right extension if missing."""
    os.makedirs(CODE_FOLDER, exist_ok=True)
    ext = _EXT_BY_LANGUAGE.get(language.lower(), ".txt")
    if not os.path.splitext(filename)[1]:
        filename = filename + ext
    path = os.path.join(CODE_FOLDER, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        return f"Wrote code to {path}."
    except Exception as e:
        return f"Failed to write code: {e}"


def run_code(filename: str) -> str:
    """Runs a previously written code file (Python or JS) and returns its output."""
    if not os.path.splitext(filename)[1]:
        # try to find a matching file in CODE_FOLDER
        for f in os.listdir(CODE_FOLDER) if os.path.isdir(CODE_FOLDER) else []:
            if os.path.splitext(f)[0] == filename:
                filename = f
                break

    path = filename if os.path.isabs(filename) else os.path.join(CODE_FOLDER, filename)
    if not os.path.exists(path):
        return f"Couldn't find code file '{filename}' in the {CODE_FOLDER} folder."

    ext = os.path.splitext(path)[1].lower()
    cmd = _RUN_CMD_BY_EXT.get(ext)
    if not cmd:
        return f"Don't know how to run {ext} files yet (only .py and .js are supported)."

    try:
        result = subprocess.run(
            cmd + [path], capture_output=True, text=True, timeout=15,
        )
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()[:2000] or "(no output)"
        return f"Ran '{filename}'. Output:\n{output}"
    except subprocess.TimeoutExpired:
        return f"'{filename}' took too long to run (over 15 seconds) and was stopped."
    except Exception as e:
        return f"Failed to run '{filename}': {e}"


# ---------- WhatsApp ----------

def _find_contact(text: str):
    text = text.lower()
    for name, number in config.CONTACTS.items():
        if name.lower() in text:
            return name, number
    return None, None


def send_whatsapp_message(contact_name: str, message: str) -> str:
    if not config.CONTACTS:
        return "No contacts configured. Ask the user to add contacts in config.py CONTACTS."

    name, number = _find_contact(contact_name)
    if not name:
        return f"No contact named '{contact_name}' found. Ask the user to add it to config.py CONTACTS."

    try:
        import pywhatkit
    except ImportError:
        return "pywhatkit isn't installed. Tell the user to run: pip install pywhatkit"

    try:
        pywhatkit.sendwhatmsg_instantly(number, message, wait_time=15, tab_close=True)
        return f"Sent WhatsApp message to {name}: '{message}'."
    except Exception as e:
        return f"Failed to send message to {name}: {e}"


# ---------- Notes / To-Do ----------

def take_note(note_text: str) -> str:
    with open(config.NOTES_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"[{timestamp}] {note_text}\n")
    return "Note saved."


def read_notes(_: str = "") -> str:
    if not os.path.exists(config.NOTES_FILE):
        return "No notes found."
    with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return "Notes file is empty."
    recent = [l.strip() for l in lines[-5:]]
    return "Recent notes:\n" + "\n".join(recent)


TODO_FILE = "todo.txt"


def add_todo(task: str) -> str:
    with open(TODO_FILE, "a", encoding="utf-8") as f:
        f.write(f"[ ] {task}\n")
    return f"Added to to-do list: {task}"


def read_todos(_: str = "") -> str:
    if not os.path.exists(TODO_FILE):
        return "To-do list is empty."
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return "To-do list is empty."
    return "To-do list:\n" + "\n".join(lines)


# ---------- Timers / Reminders ----------

def set_timer(seconds: int, label: str = "Timer") -> str:
    """Starts a background timer that beeps and shows a popup after the given seconds."""
    def _fire():
        try:
            import winsound
            winsound.Beep(1000, 700)
        except Exception:
            pass
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"{label} is up!", "NOVA Timer", 0x40 | 0x1000)
        except Exception:
            pass

    threading.Timer(seconds, _fire).start()
    minutes = seconds // 60
    return f"Timer set for {seconds} seconds (~{minutes} min) labeled '{label}'."


# ---------- Info ----------

def get_datetime(_: str = "") -> str:
    now = datetime.datetime.now()
    return f"Current time is {now.strftime('%I:%M %p')} and date is {now.strftime('%d %B, %Y')}."


def system_info(_: str = "") -> str:
    """OS info, disk space, and CPU/RAM/battery if psutil is available."""
    total, used, free = shutil.disk_usage("C:\\")
    free_gb = free // (2**30)
    total_gb = total // (2**30)
    base = (f"{platform.system()} {platform.release()}, machine {platform.machine()}. "
            f"C drive: {free_gb} GB free of {total_gb} GB total.")

    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        extra = f" CPU usage: {cpu}%. RAM usage: {ram}%."
        battery = psutil.sensors_battery()
        if battery:
            extra += f" Battery: {battery.percent}%{' (charging)' if battery.power_plugged else ' (on battery)'}."
        return base + extra
    except ImportError:
        return base + " (Install psutil for CPU/RAM/battery info: pip install psutil)"


# ---------- Schema for the Groq API (OpenAI-compatible function calling format) ----------

def _tool(name, description, properties, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


TOOLS_SCHEMA = [
    _tool("open_app", "Open any application installed on the laptop by its name (e.g. chrome, notepad, vs code, spotify).",
          {"app_name": {"type": "string", "description": "Name of the app to open"}}, ["app_name"]),

    _tool("close_app", "Force-close a running application by name.",
          {"app_name": {"type": "string", "description": "Name of the app to close"}}, ["app_name"]),

    _tool("system_control", "Control PC power state: shutdown, restart, lock, or cancel_shutdown. ALWAYS confirm with the user before calling shutdown or restart.",
          {"action": {"type": "string", "enum": ["shutdown", "restart", "lock", "cancel_shutdown"]}}, ["action"]),

    _tool("control_volume", "Adjust system volume: up, down, mute, or unmute.",
          {"action": {"type": "string", "enum": ["up", "down", "mute", "unmute"]}}, ["action"]),

    _tool("web_search", "Search Google for something and open results in the browser.",
          {"query": {"type": "string", "description": "What to search for"}}, ["query"]),

    _tool("open_website", "Open a specific website URL in the browser.",
          {"url": {"type": "string", "description": "Website URL or domain, e.g. github.com"}}, ["url"]),

    _tool("play_youtube", "Directly play a song or video on YouTube (auto-plays the top result).",
          {"query": {"type": "string", "description": "Song or video to play"}}, ["query"]),

    _tool("open_folder", "Open a folder by name (checks configured folders, then Desktop/Documents/Downloads).",
          {"folder_name": {"type": "string", "description": "Name of the folder to open"}}, ["folder_name"]),

    _tool("create_folder", "Create a new folder.",
          {
              "folder_name": {"type": "string", "description": "Name of the new folder"},
              "location": {"type": "string", "description": "Where to create it — a configured folder name (e.g. 'desktop') or full path. Defaults to Desktop."},
          }, ["folder_name"]),

    _tool("rename_item", "Rename an existing file or folder.",
          {
              "current_name": {"type": "string", "description": "Current name of the file/folder to find"},
              "new_name": {"type": "string", "description": "The new name"},
          }, ["current_name", "new_name"]),

    _tool("move_item", "Move a file or folder to a different location.",
          {
              "item_name": {"type": "string", "description": "Name of the file/folder to move"},
              "destination": {"type": "string", "description": "Destination — a configured folder name or full path"},
          }, ["item_name", "destination"]),

    _tool("copy_item", "Copy a file or folder to a different location.",
          {
              "item_name": {"type": "string", "description": "Name of the file/folder to copy"},
              "destination": {"type": "string", "description": "Destination — a configured folder name or full path"},
          }, ["item_name", "destination"]),

    _tool("delete_item", "Permanently delete a file or folder. NEVER call this without first asking the user to confirm in words, then only call with confirmed=true after they explicitly say yes.",
          {
              "item_name": {"type": "string", "description": "Name of the file/folder to delete"},
              "confirmed": {"type": "boolean", "description": "Must be true — only set true after explicit user confirmation"},
          }, ["item_name"]),

    _tool("take_screenshot", "Take a screenshot of the current screen and save it locally.", {}),

    _tool("read_document", "Read and return the text content of a Word (.docx), PowerPoint (.pptx), PDF, or text file found by name.",
          {"file_name": {"type": "string", "description": "Name of the document to read (with or without extension)"}}, ["file_name"]),

    _tool("write_code", "Write code to a new file, saved in the local 'code' folder.",
          {
              "filename": {"type": "string", "description": "Name for the code file (extension added automatically if omitted)"},
              "code": {"type": "string", "description": "The full code content to write"},
              "language": {"type": "string", "description": "Programming language, e.g. python, javascript, html, css, c, cpp, java", "enum": ["python", "javascript", "html", "css", "c", "cpp", "java"]},
          }, ["filename", "code"]),

    _tool("run_code", "Run a previously written code file (.py or .js) and return its output.",
          {"filename": {"type": "string", "description": "Name of the code file to run (must already exist in the code folder)"}}, ["filename"]),

    _tool("send_whatsapp_message", "Send a WhatsApp message to a saved contact. Requires WhatsApp Web logged in on the default browser.",
          {
              "contact_name": {"type": "string", "description": "Name of the contact (must match config.py CONTACTS)"},
              "message": {"type": "string", "description": "The message text to send"},
          }, ["contact_name", "message"]),

    _tool("take_note", "Save a short text note locally for the user.",
          {"note_text": {"type": "string", "description": "The note content"}}, ["note_text"]),

    _tool("read_notes", "Read back the user's most recently saved notes.", {}),

    _tool("add_todo", "Add a task to the user's to-do list.",
          {"task": {"type": "string", "description": "The task to add"}}, ["task"]),

    _tool("read_todos", "Read back the user's current to-do list.", {}),

    _tool("set_timer", "Set a timer/reminder that beeps and shows a popup after a delay.",
          {
              "seconds": {"type": "integer", "description": "Delay in seconds"},
              "label": {"type": "string", "description": "What the timer is for"},
          }, ["seconds"]),

    _tool("get_datetime", "Get the current date and time.", {}),

    _tool("system_info", "Get system info: OS version, disk space, CPU usage, RAM usage, and battery status.", {}),
]

TOOL_FUNCTIONS = {
    "open_app": lambda i: open_app(i["app_name"]),
    "close_app": lambda i: close_app(i["app_name"]),
    "system_control": lambda i: system_control(i["action"]),
    "control_volume": lambda i: control_volume(i["action"]),
    "web_search": lambda i: web_search(i["query"]),
    "open_website": lambda i: open_website(i["url"]),
    "play_youtube": lambda i: play_youtube(i["query"]),
    "open_folder": lambda i: open_folder(i["folder_name"]),
    "create_folder": lambda i: create_folder(i["folder_name"], i.get("location", "desktop")),
    "rename_item": lambda i: rename_item(i["current_name"], i["new_name"]),
    "move_item": lambda i: move_item(i["item_name"], i["destination"]),
    "copy_item": lambda i: copy_item(i["item_name"], i["destination"]),
    "delete_item": lambda i: delete_item(i["item_name"], i.get("confirmed", False)),
    "take_screenshot": lambda i: take_screenshot(),
    "read_document": lambda i: read_document(i["file_name"]),
    "write_code": lambda i: write_code(i["filename"], i["code"], i.get("language", "python")),
    "run_code": lambda i: run_code(i["filename"]),
    "send_whatsapp_message": lambda i: send_whatsapp_message(i["contact_name"], i["message"]),
    "take_note": lambda i: take_note(i["note_text"]),
    "read_notes": lambda i: read_notes(),
    "add_todo": lambda i: add_todo(i["task"]),
    "read_todos": lambda i: read_todos(),
    "set_timer": lambda i: set_timer(i["seconds"], i.get("label", "Timer")),
    "get_datetime": lambda i: get_datetime(),
    "system_info": lambda i: system_info(),
}


def execute(tool_name: str, tool_input: dict) -> str:
    """Runs the named tool with the given input dict, returns a result string."""
    func = TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return f"Unknown tool: {tool_name}"
    try:
        return func(tool_input)
    except Exception as e:
        return f"Error running {tool_name}: {e}"
