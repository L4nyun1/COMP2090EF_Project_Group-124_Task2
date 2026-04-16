import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading

#  Core heap algorithm (same logic as heap_sort.py)
def heapify(arr, n, root, callback=None):
    largest = root
    left    = 2 * root + 1
    right   = 2 * root + 2

    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != root:
        arr[root], arr[largest] = arr[largest], arr[root]
        if callback:
            callback(arr[:], highlight=(root, largest))
        heapify(arr, n, largest, callback)


def heap_sort_steps(arr, callback):
    """Yield intermediate states for visualization."""
    n = len(arr)
    # Phase 1
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, callback)
    # Phase 2
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        if callback:
            callback(arr[:], highlight=(0, end), sorted_from=end)
        heapify(arr, end, 0, callback)

#  Color palette
BG         = "#0f1117"
PANEL      = "#1a1d27"
ACCENT     = "#6ee7b7"      # mint green
ACCENT2    = "#f59e0b"      # amber
BAR_NORMAL = "#7ec8e3"
BAR_SWAP   = "#ef4444"      # red for swapped
BAR_SORTED = "#6ee7b7"      # mint for sorted
TEXT_MAIN  = "#e2e8f0"
TEXT_DIM   = "#64748b"
FONT_MONO  = ("Courier New", 11)
FONT_TITLE = ("Georgia", 22, "bold")
FONT_LABEL = ("Courier New", 10)

# Main Application
class HeapSortApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Heap Sort Visualizer")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(820, 600)

        self._arr          = []
        self._sorted_from  = None
        self._highlight    = ()
        self._speed        = 0.45      # seconds between frames
        self._running      = False
        self._log_lines    = []

        self._build_ui()

    # UI Construction 
    def _build_ui(self):
        # Title bar 
        title_frame = tk.Frame(self, bg=BG, pady=14)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="⬡  Heap Sort Visualizer",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack()
        tk.Label(title_frame,
                 text="Abstract Data Type: Max-Heap  │  Algorithm: O(n log n)",
                 font=("Courier New", 10), bg=BG, fg=TEXT_DIM).pack()

        # Main content row
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        left_col = tk.Frame(content, bg=BG)
        left_col.pack(side="left", fill="both", expand=True)

        right_col = tk.Frame(content, bg=BG, width=240)
        right_col.pack(side="right", fill="y", padx=(14, 0))
        right_col.pack_propagate(False)

        # Canvas for bars
        canvas_frame = tk.Frame(left_col, bg=PANEL, bd=0,
                                highlightthickness=1,
                                highlightbackground="#2d3148")
        canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg=PANEL,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Input row
        input_row = tk.Frame(left_col, bg=BG, pady=10)
        input_row.pack(fill="x")

        tk.Label(input_row, text="Enter numbers (comma-separated):",
                 font=FONT_MONO, bg=BG, fg=TEXT_MAIN).pack(side="left")

        self.entry = tk.Entry(input_row, font=FONT_MONO,
                              bg=PANEL, fg=ACCENT,
                              insertbackground=ACCENT,
                              relief="flat", bd=6, width=28)
        self.entry.insert(0, "12, 11, 13, 5, 6, 7")
        self.entry.pack(side="left", padx=(10, 0))

        # Buttons
        btn_row = tk.Frame(left_col, bg=BG, pady=4)
        btn_row.pack(fill="x")

        self._make_btn(btn_row, "▶  Sort",   self._start_sort, ACCENT)
        self._make_btn(btn_row, "⟳  Reset",  self._reset,      "#94a3b8")
        self._make_btn(btn_row, "⚡ Random",  self._random,     ACCENT2)

        # Speed slider
        speed_row = tk.Frame(left_col, bg=BG)
        speed_row.pack(fill="x")
        tk.Label(speed_row, text="Speed:", font=FONT_MONO,
                 bg=BG, fg=TEXT_DIM).pack(side="left")
        self.speed_var = tk.DoubleVar(value=0.45)
        sl = ttk.Scale(speed_row, from_=0.01, to=1.0,
                       orient="horizontal", variable=self.speed_var,
                       length=160, command=self._on_speed)
        sl.pack(side="left", padx=8)
        self.speed_label = tk.Label(speed_row, text="Medium",
                                    font=FONT_LABEL, bg=BG, fg=TEXT_DIM)
        self.speed_label.pack(side="left")

        # Right panel: legend + log
        self._build_right_panel(right_col)

    def _make_btn(self, parent, text, cmd, color):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=("Courier New", 10, "bold"),
                        bg=color, fg=BG, activebackground=BG,
                        activeforeground=color,
                        relief="flat", padx=14, pady=6,
                        cursor="hand2")
        btn.pack(side="left", padx=(0, 8))

    def _build_right_panel(self, parent):
        # Legend
        tk.Label(parent, text="LEGEND", font=("Courier New", 10, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(4, 2))
        legends = [
            (BAR_NORMAL, "Unsorted"),
            (BAR_SWAP,   "Swapping"),
            (BAR_SORTED, "Sorted"),
        ]
        for color, label in legends:
            row = tk.Frame(parent, bg=BG)
            row.pack(anchor="w", pady=1)
            tk.Label(row, bg=color, width=3, height=1).pack(side="left")
            tk.Label(row, text=f"  {label}", font=FONT_LABEL,
                     bg=BG, fg=TEXT_MAIN).pack(side="left")

        tk.Label(parent, text="COMPLEXITY", font=("Courier New", 10, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(14, 2))
        info = (
            "Build Heap: O(n)",
            "Sort Phase: O(n log n)",
            "Overall:    O(n log n)",
            "Space:      O(1)",
        )
        for line in info:
            tk.Label(parent, text=line, font=FONT_LABEL,
                     bg=BG, fg=TEXT_MAIN, anchor="w").pack(anchor="w")

        tk.Label(parent, text="STEP LOG", font=("Courier New", 10, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(14, 2))

        log_frame = tk.Frame(parent, bg=PANEL,
                             highlightthickness=1,
                             highlightbackground="#2d3148")
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, font=("Courier New", 9),
                                bg=PANEL, fg=TEXT_MAIN,
                                insertbackground=ACCENT,
                                state="disabled", wrap="word",
                                relief="flat", bd=4,
                                width=26)
        sb = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

    # Controls
    def _on_speed(self, val):
        v = float(val)
        self._speed = v
        if v < 0.1:
            label = "Fast"
        elif v < 0.6:
            label = "Medium"
        else:
            label = "Slow"
        self.speed_label.configure(text=label)

    def _parse_input(self):
        raw = self.entry.get().strip()
        try:
            nums = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if not nums:
                raise ValueError
            if len(nums) > 50:
                messagebox.showwarning("Too many values",
                                       "Please enter 50 or fewer numbers.")
                return None
            return nums
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "Please enter integers separated by commas.\n"
                                 "Example: 12, 11, 13, 5, 6, 7")
            return None

    def _reset(self):
        self._running = False
        self._arr = []
        self._sorted_from = None
        self._highlight = ()
        self._log_clear()
        self.canvas.delete("all")
        nums = self._parse_input()
        if nums:
            self._arr = nums
            self._draw(self._arr)

    def _random(self):
        import random
        nums = random.sample(range(1, 100), 12)
        self.entry.delete(0, "end")
        self.entry.insert(0, ", ".join(map(str, nums)))
        self._reset()

    def _start_sort(self):
        if self._running:
            return
        nums = self._parse_input()
        if not nums:
            return
        self._arr = nums[:]
        self._sorted_from = None
        self._highlight = ()
        self._log_clear()
        self._log(f"Input: {self._arr}\n")
        self._draw(self._arr)
        self._running = True
        t = threading.Thread(target=self._run_sort, daemon=True)
        t.start()

    def _run_sort(self):
        arr = self._arr[:]
        step = [0]

        def cb(state, highlight=(), sorted_from=None):
            if not self._running:
                return
            self._highlight    = highlight
            self._sorted_from  = sorted_from
            step[0] += 1
            if highlight:
                a, b = highlight
                self._log(f"Step {step[0]:>3}: swap [{a}]={state[b]} ↔ [{b}]={state[a]}\n")
            self.after(0, lambda s=state[:]: self._draw(s))
            time.sleep(self._speed)

        heap_sort_steps(arr, cb)
        self._running     = False
        self._highlight   = ()
        self._sorted_from = 0
        self.after(0, lambda: self._draw(arr))
        self._log(f"\nSorted: {arr}\n✓ Done!\n")

    # Drawing
    def _draw(self, arr):
        self.canvas.delete("all")
        if not arr:
            return

        W = self.canvas.winfo_width()  or 600
        H = self.canvas.winfo_height() or 360
        n = len(arr)
        pad_x, pad_top, pad_bot = 20, 20, 40
        max_val  = max(arr) if arr else 1
        bar_w    = (W - 2 * pad_x) / n
        gap      = max(2, bar_w * 0.12)

        sorted_start = self._sorted_from if self._sorted_from is not None else n

        for i, v in enumerate(arr):
            x1 = pad_x + i * bar_w + gap / 2
            x2 = pad_x + (i + 1) * bar_w - gap / 2
            bar_h = (v / max_val) * (H - pad_top - pad_bot)
            y1 = H - pad_bot - bar_h
            y2 = H - pad_bot

            if i >= sorted_start:
                color = BAR_SORTED
            elif i in self._highlight:
                color = BAR_SWAP
            else:
                color = BAR_NORMAL

            # bar with rounded-top look via two overlapping shapes
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=color, outline="",
                                         tags="bar")
            # value label
            mid_x = (x1 + x2) / 2
            self.canvas.create_text(mid_x, y1 - 8,
                                    text=str(v),
                                    font=("Courier New", max(7, int(bar_w * 0.4))),
                                    fill=TEXT_MAIN)
            # index label
            self.canvas.create_text(mid_x, H - pad_bot + 14,
                                    text=str(i),
                                    font=("Courier New", 8),
                                    fill=TEXT_DIM)

    # Log helpers
    def _log(self, msg):
        def _insert():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.after(0, _insert)

    def _log_clear(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

# main program
if __name__ == "__main__":
    app = HeapSortApp()
    # Draw initial default data after window is ready
    app.update_idletasks()
    nums = [int(x.strip()) for x in "12, 11, 13, 5, 6, 7".split(",")]
    app._arr = nums
    app.after(100, lambda: app._draw(nums))
    app.mainloop()
