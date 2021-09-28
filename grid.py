"""
화면 크기에 맞춰서 그리드를 그려주는 파일
"""
from typing import Dict, List, Tuple
from tkinter import Tk, Text  # or(from Tkinter import Tk) on Python 2.x
import tkinter as tk
import string
import keyboard
import pyautogui as pag

""" TODO: 듀얼 모니터에서 사용 가능하도록 만들기
def fullscreen(win: Tk):
    monitors = screeninfo.get_monitors()
    width = 0
    for monitor in monitors:
        width += monitor.width
        
    win.geometry()
"""


class Grid(Tk):

    def __init__(self, cell_per_pixel=10, toggle_key="ctrl+windows+v", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_visibility(self)
        # 배경 투명하게

        self.config(bg='#add123')

        # Create a transparent window
        self.wm_attributes('-transparentcolor', '#add123')

        # 전체 화면 모드
        self.attributes("-fullscreen", True)

        self.cell_per_pixel = cell_per_pixel
        self.cell_positions: Dict[str, Tuple[int, int]] = {}
        cols, rows = self.grid_size()
        self.cs = self.combination_size(cols, rows)

        self.hidden = False
        self.toggle_key = toggle_key
        self.clear_pressed()
        keyboard.add_hotkey(self.toggle_key, self.toggle, suppress=True, timeout=0.5, trigger_on_release=True)
        self.hook = keyboard.on_press(self.add_pressed, suppress=True)
        
        self.toggle()
        

    def add_pressed(self, event: keyboard.KeyboardEvent):
        if not self.hidden:
            self.pressed.append(event.name)
            
        else:
            self.clear_pressed()

        if not self.hidden and event.name == 'esc':
            self.toggle(False)
            return
        
        if len(self.pressed) >= self.cs:
            self.click("".join(self.pressed))
            self.clear_pressed()
            self.toggle()

    def clear_pressed(self):
        self.pressed: List[str] = []

    def toggle(self, value=None):
        
        if value:
            self.hidden = not value
        
        if self.hidden:
            self.deiconify()
            #self.focus_set()
            self.hook = keyboard.on_press(self.add_pressed, suppress=True)
        else:
            self.withdraw()
            keyboard.unhook(self.hook)
            self.hook = None

        self.hidden = not self.hidden

    def click(self, cell: str):

        try:
            x, y = self.cell_positions[cell]
            pag.click(x,y)
            print(f"click {x}. {y}")
        except KeyError:
            print(f"No key")

    def run(self):
        self.mainloop()

    def grid_size(self) -> Tuple[int, int]:
        h = self.winfo_height()
        w = self.winfo_width()
        return int(w/self.cell_per_pixel), int(h / self.cell_per_pixel)

    def combination_size(self, cols: int, rows: int) -> int:
        size = 1
        while pow(len(string.ascii_lowercase), size) < cols * rows:
            size += 1
        return size

    def combination_generator(self, combination_size: int, cols: int, rows: int) -> List[str]:
        indexes = [0 for i in range(combination_size)]

        count = 0
        while count < cols * rows:
            text = "".join([string.ascii_lowercase[x] for x in indexes])
            yield text

            indexes[0] += 1
            for i, index in enumerate(indexes):
                if index >= len(string.ascii_lowercase):
                    indexes[i] = 0
                    indexes[i+1] += 1

            count += 1

    def create_grid(self):
        cpp = self.cell_per_pixel
        h = self.winfo_height()
        w = self.winfo_width()
        cols, rows = self.grid_size()

        self.canvas = tk.Canvas(self)
        self.canvas.configure(bg="#add123")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

        for x in range(1, cols):
            self.canvas.create_line(x*cpp, 0, x*cpp, h, width=2, fill="red")

        for y in range(1, rows):
            self.canvas.create_line(0, y*cpp, w, y*cpp, width=2, fill="red")

        cs = self.cs
        cg = self.combination_generator(cs, cols, rows)
        for x in range(cols):
            for y in range(rows):
                combination = next(cg)
                cx = x*cpp + cpp/2
                cy = y*cpp + cpp/2

                self.canvas.create_text(
                    cx,
                    cy,
                    text=combination,
                    fill="red",
                    font=("Purisa", 15))
                self.cell_positions[combination] = (cx, cy)


if __name__ == "__main__":
    grid = Grid(cell_per_pixel=40)
    grid.create_grid()
    grid.run()
