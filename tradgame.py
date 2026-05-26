import tkinter as tk
import threading
import time
import mss
import cv2
import numpy as np
import easyocr
from deep_translator import GoogleTranslator

# =========================
# OCR
# =========================
reader = easyocr.Reader(['en', 'it'], gpu=False)

# =========================
# STATE
# =========================
running = False
instances = []

bg_opacity = 0.85
bg_color = "black"
text_color = "white"

source_lang = "auto"
target_lang = "it"

settings_win = None

# =========================
# MAIN APP
# =========================
app = tk.Tk()
app.title("Translator PRO")
app.geometry("400x250")
app.configure(bg="#111")

tk.Label(app, text="TRANSLATOR PRO", fg="white", bg="#111",
         font=("Arial", 16, "bold")).pack(pady=10)

status = tk.Label(app, text="READY", fg="lime", bg="#111")
status.pack()

# =========================
# UPDATE ALL
# =========================
def update_all_boxes():
    for b in instances:
        b.update_style()

# =========================
# TRANSLATOR BOX
# =========================
class TranslatorBox:

    def __init__(self, region, x, y):

        self.region = region
        self.last_text = ""

        self.drag_enabled = True
        self.drag_data = {"x": 0, "y": 0}

        self.win = tk.Toplevel(app)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", bg_opacity)
        self.win.configure(bg=bg_color)
        self.win.geometry(f"800x150+{x}+{y}")

        frame = tk.Frame(self.win, bg=bg_color)
        frame.pack(fill="both", expand=True)

        self.label = tk.Label(
            frame,
            text="Waiting OCR...",
            fg=text_color,
            bg=bg_color,
            font=("Arial", 16),
            wraplength=760,
            justify="left"
        )
        self.label.pack(fill="both", expand=True, padx=10, pady=10)

        self.lock_btn = tk.Button(
            frame,
            text="🔓",
            command=self.toggle_lock,
            bg="#222",
            fg="white",
            bd=0
        )
        self.lock_btn.place(x=5, y=5)

        self.win.bind("<ButtonPress-1>", self.start_move)
        self.win.bind("<B1-Motion>", self.do_move)

    def toggle_lock(self):
        self.drag_enabled = not self.drag_enabled
        self.lock_btn.config(text="🔓" if self.drag_enabled else "🔒")

    def start_move(self, e):
        if not self.drag_enabled:
            return
        self.drag_data["x"] = e.x_root
        self.drag_data["y"] = e.y_root

    def do_move(self, e):
        if not self.drag_enabled:
            return

        dx = e.x_root - self.drag_data["x"]
        dy = e.y_root - self.drag_data["y"]

        x = self.win.winfo_x() + dx
        y = self.win.winfo_y() + dy

        self.win.geometry(f"+{x}+{y}")

        self.drag_data["x"] = e.x_root
        self.drag_data["y"] = e.y_root

    def update_style(self):
        self.win.configure(bg=bg_color)
        self.win.attributes("-alpha", bg_opacity)
        self.label.configure(bg=bg_color, fg=text_color)

    def update_text(self, text):
        self.label.config(text=text)

    def destroy(self):
        if self.win.winfo_exists():
            self.win.destroy()

# =========================
# OCR LOOP
# =========================
def loop(box):

    global running

    with mss.MSS() as sct:

        while running:

            if not box.win.winfo_exists():
                break

            try:
                img = np.array(sct.grab(box.region))
                gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                results = reader.readtext(gray)

                text = " ".join([r[1] for r in results]).strip()

            except:
                continue

            if text and text != box.last_text:

                box.last_text = text

                try:
                    translated = GoogleTranslator(
                        source=source_lang,
                        target=target_lang
                    ).translate(text)
                except:
                    translated = "ERROR"

                box.win.after(0, lambda t=translated: box.update_text(t))

            time.sleep(0.5)

# =========================
# SELECT AREA
# =========================
def select_area(callback):

    selector = tk.Toplevel(app)

    with mss.MSS() as sct:
        mon = sct.monitors[0]

    selector.geometry(f"{mon['width']}x{mon['height']}+0+0")
    selector.attributes("-alpha", 0.3)
    selector.configure(bg="gray")

    canvas = tk.Canvas(selector, cursor="cross")
    canvas.pack(fill="both", expand=True)

    sx = sy = 0
    rect = None

    def down(e):
        nonlocal sx, sy, rect
        sx, sy = e.x, e.y
        rect = canvas.create_rectangle(sx, sy, sx, sy, outline="red")

    def move(e):
        canvas.coords(rect, sx, sy, e.x, e.y)

    def up(e):

        selector.destroy()

        callback({
            "left": min(sx, e.x),
            "top": min(sy, e.y),
            "width": abs(e.x - sx),
            "height": abs(e.y - sy)
        })

    canvas.bind("<ButtonPress-1>", down)
    canvas.bind("<B1-Motion>", move)
    canvas.bind("<ButtonRelease-1>", up)

# =========================
# START
# =========================
def start():

    global running, instances

    if running:
        status.config(text="STOP FIRST", fg="red")
        return

    def ask():

        win = tk.Toplevel(app)
        win.title("Boxes")
        win.geometry("300x150")
        win.configure(bg="#111")

        tk.Label(win, text="How many boxes?", fg="white", bg="#111").pack(pady=10)

        e = tk.Entry(win, justify="center")
        e.pack()

        def go():
            try:
                count = max(1, int(e.get()))
            except:
                count = 1

            win.destroy()
            select_many(count)

        tk.Button(win, text="START", command=go).pack()

    def select_many(count):

        selected = []

        def next_r(region):
            selected.append(region)

            if len(selected) < count:
                select_area(next_r)
            else:
                launch(selected)

        select_area(next_r)

    def launch(regions):

        global running, instances

        running = True
        instances.clear()

        status.config(text="RUNNING", fg="lime")

        for i, r in enumerate(regions):

            box = TranslatorBox(r, 100 + i * 40, 100 + i * 40)
            instances.append(box)

            threading.Thread(target=loop, args=(box,), daemon=True).start()

    ask()

# =========================
# STOP
# =========================
def stop():

    global running, instances

    running = False

    for b in instances:
        b.destroy()

    instances.clear()

    status.config(text="STOPPED", fg="orange")

# =========================
# SETTINGS (SINGLE INSTANCE FIXED)
# =========================
def settings():

    global bg_opacity, bg_color, text_color, source_lang, target_lang
    global settings_win

    if settings_win and settings_win.winfo_exists():
        settings_win.lift()
        return

    settings_win = tk.Toplevel(app)
    settings_win.title("Settings")
    settings_win.geometry("380x550")
    settings_win.configure(bg="#111")

    def on_close():
        global settings_win
        if settings_win and settings_win.winfo_exists():
            settings_win.destroy()
        settings_win = None

    settings_win.protocol("WM_DELETE_WINDOW", on_close)

    # ================= OPACITY =================
    tk.Label(settings_win, text="Opacity", fg="cyan", bg="#111").pack()

    op = tk.Scale(settings_win, from_=0.3, to=1.0,
                  resolution=0.05, orient="horizontal")
    op.set(bg_opacity)
    op.pack(fill="x")

    def set_op(v):
        global bg_opacity
        bg_opacity = float(v)
        update_all_boxes()

    op.config(command=set_op)

    # ================= BACKGROUND =================
    tk.Label(settings_win, text="Background", fg="lime", bg="#111").pack()

    def set_bg(c):
        global bg_color
        bg_color = c
        update_all_boxes()

    tk.Button(settings_win, text="Black", command=lambda: set_bg("black")).pack(fill="x")
    tk.Button(settings_win, text="Gray", command=lambda: set_bg("#222")).pack(fill="x")

    # ================= TEXT =================
    tk.Label(settings_win, text="Text Color", fg="orange", bg="#111").pack()

    def set_text(c):
        global text_color
        text_color = c
        update_all_boxes()

    tk.Button(settings_win, text="White", command=lambda: set_text("white")).pack(fill="x")
    tk.Button(settings_win, text="Green", command=lambda: set_text("lime")).pack(fill="x")

    # ================= LANG =================
    tk.Label(settings_win, text="Languages", fg="white", bg="#111").pack()

    def set_lang(s, t):
        global source_lang, target_lang
        source_lang = s
        target_lang = t

    tk.Button(settings_win, text="AUTO → IT", command=lambda: set_lang("auto", "it")).pack(fill="x")
    tk.Button(settings_win, text="EN → IT", command=lambda: set_lang("en", "it")).pack(fill="x")
    tk.Button(settings_win, text="IT → EN", command=lambda: set_lang("it", "en")).pack(fill="x")

# =========================
# UI
# =========================
tk.Button(app, text="START", command=start).pack(fill="x", padx=20, pady=5)
tk.Button(app, text="STOP", command=stop).pack(fill="x", padx=20, pady=5)
tk.Button(app, text="SETTINGS", command=settings).pack(fill="x", padx=20, pady=5)

app.mainloop()
