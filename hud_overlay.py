import tkinter as tk
import threading
import queue
import ctypes
import math

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

class GameOverlay:
    def __init__(self):
        self.cmd_queue = queue.Queue()
        self.thread = threading.Thread(target=self._run_ui, daemon=True)
        self.thread.start()

    def update_score(self, score, max_score, length, icons_left):
        self.cmd_queue.put(('score', (score, max_score, length, icons_left)))

    def update_status(self, text):
        self.cmd_queue.put(('status', text))

    def update_fruit_position(self, x, y, size_w, size_h):
        self.cmd_queue.put(('fruit', (x, y, size_w, size_h)))

    def update_center_text(self, text, color="red"):
        self.cmd_queue.put(('center_text', (text, color)))

    def update_boundary(self, left, top, right, bottom):
        self.cmd_queue.put(('boundary', (left, top, right, bottom)))

    def play_easter_egg_animation(self):
        self.cmd_queue.put(('easter_egg', None))

    def stop(self):
        self.cmd_queue.put(('stop', None))

    def _run_ui(self):
        self.root = tk.Tk()
        self.root.title("Desktop Snake HUD")
        self.root.overrideredirect(True)
        
        # Transparent color key
        trans_color = '#010101'
        self.root.config(bg=trans_color)
        self.root.wm_attributes('-transparentcolor', trans_color)
        self.root.wm_attributes('-topmost', True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Click-through window
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height, bg=trans_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Boundary Rects for visual game area
        self.boundary_outer = self.canvas.create_rectangle(0, 0, 0, 0, outline="#ff0044", width=6)
        self.boundary_inner = self.canvas.create_rectangle(0, 0, 0, 0, outline="#ffbbcc", width=2)

        # UI Elements
        self.score_text = self.canvas.create_text(screen_width - 30,screen_height - 20, text="Score: 0", font=("Consolas", 20, "bold"), fill="#00FFaa", anchor="se")
        self.status_text = self.canvas.create_text(screen_width - 30, 5, text="", font=("Consolas", 15, "bold"), fill="yellow", anchor="ne")
        self.center_text = self.canvas.create_text(screen_width//2, screen_height//2, text="", font=("Consolas", 120, "bold"), fill="red")
        
        self.fruit_glow_items = []
        self._glow_phase = 0.0

        self._process_queue()
        self._animate_glow()
        self.root.mainloop()

    def _process_queue(self):
        try:
            while True:
                cmd, data = self.cmd_queue.get_nowait()
                if cmd == 'stop':
                    self.root.destroy()
                    return
                elif cmd == 'score':
                    score, max_score, length, icons_left = data
                    text = f"Score: {score}/{max_score} | Length: {length} | Icons Left: {icons_left}"
                    self.canvas.itemconfig(self.score_text, text=text)
                elif cmd == 'status':
                    self.canvas.itemconfig(self.status_text, text=data)
                elif cmd == 'center_text':
                    self.canvas.itemconfig(self.center_text, text=data[0], fill=data[1])
                elif cmd == 'boundary':
                    left, top, right, bottom = data
                    self.canvas.coords(self.boundary_outer, left, top, right, bottom)
                    self.canvas.coords(self.boundary_inner, left, top, right, bottom)
                elif cmd == 'fruit':
                    self.fruit_data = data
                elif cmd == 'easter_egg':
                    self.fruit_data = None
                    for item in self.fruit_glow_items:
                        self.canvas.delete(item)
                    self.fruit_glow_items.clear()
                    self._start_easter_egg()
        except queue.Empty:
            pass
        
        if self.root.winfo_exists():
            self.root.after(30, self._process_queue)

    def _start_easter_egg(self):
        import random
        self.confetti_items = []
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
        # Glowing winning text
        self.canvas.create_text(screen_width//2, screen_height//3, text="VICTORY", font=("Consolas", 100, "bold"), fill="gold")
        
        for _ in range(200):
            x = random.randint(0, screen_width)
            y = random.randint(-screen_height, 0)
            size = random.randint(10, 20)
            color = random.choice(colors)
            item = self.canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
            dx = random.randint(-4, 4)
            dy = random.randint(8, 20)
            self.confetti_items.append({"id": item, "dx": dx, "dy": dy})
        self._animate_easter_egg()

    def _animate_easter_egg(self):
        if not hasattr(self, 'root') or not self.root.winfo_exists():
            return
        screen_height = self.root.winfo_screenheight()
        for conf in self.confetti_items:
            self.canvas.move(conf["id"], conf["dx"], conf["dy"])
            coords = self.canvas.coords(conf["id"])
            if coords and coords[1] > screen_height:
                self.canvas.move(conf["id"], 0, -screen_height - 100)
        self.root.after(30, self._animate_easter_egg)

    def _animate_glow(self):
        for item in self.fruit_glow_items:
            self.canvas.delete(item)
        self.fruit_glow_items.clear()

        if hasattr(self, 'fruit_data') and self.fruit_data is not None and self.fruit_data[0] is not None:
            x, y, size_w, size_h = self.fruit_data
            y=y
            rx = size_w // 2 + 5
            ry = size_h // 2 + 5
            
            # Pulsing logic
            pulse = math.sin(self._glow_phase) * 0.5 + 0.5 # 0.0 to 1.0
            radius_offset = int(pulse * 10)
            
            # Base rectangle
            y_shrink = 20  # Decreases the vertical length of the rectangle
            c1 = self.canvas.create_rectangle(x - rx - radius_offset, y - ry + y_shrink - radius_offset, 
                                         x + rx + radius_offset, y + ry - y_shrink + radius_offset, 
                                         outline="#00ffff", width=4)
                                         
            c2 = self.canvas.create_rectangle(x - rx - radius_offset//2, y - ry + y_shrink - radius_offset//2, 
                                         x + rx + radius_offset//2, y + ry - y_shrink + radius_offset//2, 
                                         outline="#ff00ff", width=2)
            self.fruit_glow_items.extend([c1, c2])

        self._glow_phase += 0.15
        if self.root.winfo_exists():
            self.root.after(50, self._animate_glow)
