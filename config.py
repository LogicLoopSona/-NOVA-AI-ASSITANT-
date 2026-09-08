"""
Configuration for the Voice Assistant.
Edit this file to customize behavior without touching main logic.
"""

# Loads variables from a local ".env" file (like GROQ_API_KEY=...) if one
# exists. Copy ".env.example" to ".env" and put your real key there — ".env"
# is git-ignored so it never gets committed. Safe to skip if you'd rather set
# GROQ_API_KEY as a real Windows environment variable instead.
try:
    import os as _os
    from dotenv import load_dotenv
    _env_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".env")
    load_dotenv(_env_path)
except ImportError:
    pass

# Assistant's name — used in greetings and replies.
ASSISTANT_NAME = "NOVA"

# ---------- AI Brain — Groq API (100% FREE, no credit card needed) ----------
# Get a free key from https://console.groq.com -> API Keys
# RECOMMENDED (safer): set it as a Windows environment variable named
# GROQ_API_KEY instead of pasting it here. If that variable is set,
# it's used automatically and this value below is ignored.
# ---------- AI Brain — Groq API (100% FREE, no credit card needed) ----------
# Get a free key from https://console.groq.com -> API Keys
# Put it in a local ".env" file as GROQ_API_KEY=gsk_... (see .env.example) —
# NEVER paste the real key directly in this file if this project goes on GitHub.
GROQ_API_KEY = ""  # only used if no .env file and no environment variable are set

# Groq deprecated llama-3.1-8b-instant & llama-3.3-70b-versatile (June 2026).
# openai/gpt-oss-20b is their recommended free replacement — fast, smart, and
# supports tool calling well. If replies feel too simple, try "openai/gpt-oss-120b"
# (smarter, but uses up the free daily budget faster).
MODEL = "openai/gpt-oss-20b"


def get_api_key() -> str:
    import os
    return os.environ.get("GROQ_API_KEY") or GROQ_API_KEY

# Name the assistant responds to (optional wake word before each command).
# Set WAKE_WORD_REQUIRED = False if you just want it to always listen for commands.
WAKE_WORD_REQUIRED = False
WAKE_WORD = "hey nova"

# Text-to-speech settings
# TTS_ENGINE = "gtts" uses Google's free Text-to-Speech (much more natural than
# the robotic Windows voice, and more reliable than Edge's unofficial API).
# Falls back to "pyttsx3" (robotic Windows voice) automatically if offline.
# Set TTS_ENGINE = "pyttsx3" to always use the old robotic voice instead.
TTS_ENGINE = "gtts"
GTTS_LANG = "hi"     # "hi" = Hindi accent (good for Hinglish), "en" = English accent

# Fallback (pyttsx3) settings — only used if gTTS fails or TTS_ENGINE = "pyttsx3"
TTS_RATE = 175          # words per minute
TTS_VOLUME = 1.0        # 0.0 to 1.0
TTS_VOICE_INDEX = 0     # 0 = default voice, 1 = usually the alternate (e.g. female) voice on Windows

# Speech recognition settings
LISTEN_TIMEOUT = 5          # seconds to wait for speech to start
PHRASE_TIME_LIMIT = 8       # max seconds for a single command
ENERGY_THRESHOLD = 300      # mic sensitivity (lower = more sensitive). Auto-adjusts too.

# Where notes taken via voice ("note likho...") get saved
NOTES_FILE = "notes.txt"

# App paths — EDIT these if an app doesn't open correctly on your PC.
# Most common apps work with just the .exe name if they're in PATH.
# For apps not in PATH, put the full path e.g. r"C:\Program Files\App\app.exe"
APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "vscode": "code.exe",
    "vs code": "code.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "spotify": "spotify.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "settings": "start ms-settings:",
}

# Fallback install locations for common apps, checked when the plain .exe
# name isn't found in PATH (this is why "chrome.exe" alone often fails).
# %ProgramFiles%, %LocalAppData% etc. are expanded automatically.
COMMON_INSTALL_PATHS = {
    "chrome.exe": [
        r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
        r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
        r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
    ],
    "msedge.exe": [
        r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    ],
    "code.exe": [
        r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe",
        r"%ProgramFiles%\Microsoft VS Code\Code.exe",
    ],
    "spotify.exe": [
        r"%AppData%\Spotify\Spotify.exe",
    ],
    "winword.exe": [
        r"%ProgramFiles%\Microsoft Office\root\Office16\WINWORD.EXE",
        r"%ProgramFiles(x86)%\Microsoft Office\root\Office16\WINWORD.EXE",
    ],
    "excel.exe": [
        r"%ProgramFiles%\Microsoft Office\root\Office16\EXCEL.EXE",
        r"%ProgramFiles(x86)%\Microsoft Office\root\Office16\EXCEL.EXE",
    ],
    "powerpnt.exe": [
        r"%ProgramFiles%\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"%ProgramFiles(x86)%\Microsoft Office\root\Office16\POWERPNT.EXE",
    ],
}

# Extra folders to search for installed apps when a name isn't in APP_PATHS above.
# NOVA will look through Start Menu shortcuts here and launch the closest match.
START_MENU_SEARCH_DIRS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    r"%APPDATA%\Microsoft\Windows\Start Menu\Programs",
]

# Named folders you want to open by voice, e.g. "open projects folder".
# Add your own — key is the spoken name, value is the full path.
FOLDER_PATHS = {
    "desktop": r"C:\Users\snagw\OneDrive\Desktop",
    "chatbot": r"C:\Users\snagw\OneDrive\Desktop\chatbot",
    "dsa": r"C:\Users\snagw\OneDrive\Desktop\Dsa_c",
    "mental health chatbot": r"C:\Users\snagw\OneDrive\Desktop\Euron_Mental_Health_Chatbot",
    "html": r"C:\Users\snagw\OneDrive\Desktop\HTML",
    "html css js projects": r"C:\Users\snagw\OneDrive\Desktop\HTML-CSS-JS-PROJECTS-adc2d77224586bde6e846aa4e9bcc6027644e033",
    "jarvis": r"C:\Users\snagw\OneDrive\Desktop\jarvis-ai-assistant-main",
    "mam file": r"C:\Users\snagw\OneDrive\Desktop\mam_file",
    "mini project": r"C:\Users\snagw\OneDrive\Desktop\my_mini_project",
    "nova": r"C:\Users\snagw\OneDrive\Desktop\Nova",
    "project 2": r"C:\Users\snagw\OneDrive\Desktop\project_2",
    "project 3": r"C:\Users\snagw\OneDrive\Desktop\project_3",
   
}

# Saved website shortcuts — say the name and NOVA opens the exact link.
# Add more anytime: "spoken name": "full URL"
WEBSITES = {
    "linkedin": "https://www.linkedin.com/in/sona-gupta-260170338/",
    "github new repo": "https://github.com/new",
    "whatsapp": "https://web.whatsapp.com/",
    "onedrive": "https://onedrive.live.com/?id=F8B8052791795195%21sf51363e6cd7243c6a593bb3926f79c4c&cid=F8B8052791795195",
    "ai for all gmail": "https://mail.google.com/mail/u/1/#inbox",
    "gmail": "https://mail.google.com/mail/u/0/?hl=en#inbox",
    "youtube": "https://www.youtube.com/",
    "colab": "https://colab.research.google.com/drive/1t5OmEbv75ypygQFn3PxLb3QoI_w606q3?usp=sharing",
    "classroom": "https://classroom.google.com/c/Nzk4NDM2MDkzODU0",
    "leetcode": "https://leetcode.com/problemset/",
}

# Folder where voice-triggered screenshots get saved.
SCREENSHOTS_FOLDER = "screenshots"

# Add people you want to message by voice. Phone numbers MUST include country
# code with a "+", e.g. "+91XXXXXXXXXX" for India.
# IMPORTANT: WhatsApp Web (web.whatsapp.com) must already be logged in on your
# default browser for message-sending to work.
CONTACTS = {
    "medhak": "+917906481308",
    "princess": "+918864957355",
    "panda": "+917409932252",
    "maa": "+918650170993",
    "papa 2": "+919725397854",
    "papa": "+919316646697",
    "muneem": "+918630443140",
    "mona": "+919719214744",
    "bhai": "+919389032622",
    "ankit bhai": "+918273134502",
    "deepa": "+918273964016",
    "sher": "+917830671532",
    "pawan": "+919837113680",
    "bm sir": "+919389927877",
    "chirag": "+919558443810",
    "karishma": "+917417563930",
    "sakshi": "+919389013105",
}
