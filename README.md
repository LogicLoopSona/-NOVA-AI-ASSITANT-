NOVA — AI-Powered Voice Assistant for Windows

NOVA is a JARVIS-inspired personal voice assistant that lets you control your Windows laptop entirely through natural speech — in Hindi, English, or Hinglish. Unlike traditional voice assistants built on rigid keyword-matching, NOVA uses a large language model (via the Groq API, running Llama/GPT-OSS models) as its reasoning engine, allowing it to understand natural, conversational commands and decide on its own whether to simply chat or invoke a tool to take real action on the system.

Architecture

Voice input is captured via the microphone and transcribed using Google's Speech Recognition API. The transcribed text is sent to the LLM along with a set of defined tools. The model performs intent detection: if the request is casual conversation, it responds directly; if it requires action, it calls the appropriate tool through OpenAI-compatible function calling. Tool results are fed back to the model, which then generates a natural-language response that's converted to speech using Google Text-to-Speech (gTTS) and played back to the user. The entire interaction is visualized through a custom Tkinter GUI featuring an animated, color-coded pulsing orb that reflects NOVA's current state (idle, listening, thinking, speaking).

Capabilities
Open/close applications, folders, and saved website shortcuts by name
Create, rename, move, copy, and safely delete files/folders (with mandatory user confirmation before destructive actions)
Read and summarize Word, PowerPoint, PDF, and text documents
Write and execute Python/JavaScript code on request
Send WhatsApp messages to saved contacts
Take screenshots, set timers/reminders, manage to-do lists and notes
Report system stats (CPU, RAM, battery, disk space)
Control system volume and power state (shutdown/restart/lock)
Runs silently in the background with Windows autostart support — no terminal window required
Tech Stack

Python · Groq API (LLM inference) · SpeechRecognition · gTTS · Tkinter · python-docx/pptx/pypdf · pywhatkit · psutil

Why I Built This

As part of my journey toward becoming an AI/ML engineer, I wanted to move beyond tutorial-style projects and build something genuinely useful in daily life — a hands-free assistant that demonstrates practical LLM tool-calling, speech pipelines, and real system integration, not just a chatbot in a browser tab.
