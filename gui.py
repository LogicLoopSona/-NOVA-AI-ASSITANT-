"""
NOVA's visual interface — a JARVIS-style animated glowing circle.
Uses tkinter (built into Python, no extra install needed).

States:
  idle      -> slow blue breathing pulse
  listening -> green pulse + rotating ring (mic is on)
  thinking  -> orange pulse + rotating ring (waiting on the AI)
  speaking  -> purple pulse (NOVA is talking)
"""

import math
import tkinter as tk

COLORS = {
    "idle": "#00d4ff",
    "listening": "#00ff88",
    "thinking": "#ffaa00",
    "speaking": "#a855f7",
    "error": "#ff4444",
}

STATUS_TEXT = {
    "idle": "Ready",
    "listening": "Listening...",
    "thinking": "Thinking...",
    "speaking": "Speaking...",
    "error": "Error — check nova_log.txt",
}


class NovaGUI:
    def __init__(self, assistant_name="NOVA"):
        self.state = "idle"
        self._angle = 0
        self._pulse = 0.0

        self.root = tk.Tk()
        self.root.title(assistant_name)
        self.root.geometry("380x420")
        self.root.configure(bg="#0a0a1a")
        self.root.attributes("-topmost", False)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=380, height=340, bg="#0a0a1a", highlightthickness=0)
        self.canvas.pack()

        self.name_label = tk.Label(
            self.root, text=assistant_name, fg="#e0e0e0", bg="#0a0a1a",
            font=("Segoe UI", 18, "bold"),
        )
        self.name_label.pack(pady=(5, 0))

        self.status_label = tk.Label(
            self.root, text="Ready", fg="#888888", bg="#0a0a1a",
            font=("Segoe UI", 11),
        )
        self.status_label.pack()

        self.transcript_label = tk.Label(
            self.root, text="", fg="#666666", bg="#0a0a1a",
            font=("Segoe UI", 9), wraplength=340, justify="center",
        )
        self.transcript_label.pack(pady=(5, 0))

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._closing = False

        self._animate()

    # ---------- Called from the assistant thread (thread-safe via .after) ----------

    def set_state(self, state: str):
        self.state = state
        text = STATUS_TEXT.get(state, state)
        self.root.after(0, lambda: self.status_label.config(text=text, fg=COLORS.get(state, "#888888")))

    def set_transcript(self, text: str):
        display = text if len(text) < 80 else text[:77] + "..."
        self.root.after(0, lambda: self.transcript_label.config(text=display))

    def close(self):
        self._closing = True
        self.root.after(0, self.root.destroy)

    # ---------- Internal ----------

    def _on_close(self):
        # User clicked the window's X button — exit the whole process.
        self._closing = True
        self.root.destroy()
        import os
        os._exit(0)

    def _animate(self):
        if self._closing:
            return
        self.canvas.delete("all")
        cx, cy = 190, 170
        base_radius = 75
        color = COLORS.get(self.state, "#00d4ff")

        self._pulse += 0.12
        if self.state == "idle":
            pulse_amt = math.sin(self._pulse * 0.4) * 4
        else:
            pulse_amt = math.sin(self._pulse) * 10
        radius = base_radius + pulse_amt

        # Outer glow rings
        for i in range(3):
            r = radius + 15 + i * 14
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=1)

        # Rotating arc while listening/thinking
        if self.state in ("listening", "thinking"):
            self._angle = (self._angle + 5) % 360
            r = radius + 30
            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=self._angle, extent=70, outline="white", width=3, style="arc",
            )
            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=self._angle + 180, extent=70, outline="white", width=3, style="arc",
            )

        # Core filled circle
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color, outline="")
        # Inner bright core
        inner = radius * 0.4
        self.canvas.create_oval(cx - inner, cy - inner, cx + inner, cy + inner, fill="#ffffff", outline="")

        self.root.after(40, self._animate)

    def run(self):
        self.root.mainloop()
