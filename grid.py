"""
화면 크기에 맞춰서 그리드를 그려주는 파일
"""
from typing import Dict, List, Optional, Tuple
from tkinter import Tk, Text  # or(from Tkinter import Tk) on Python 2.x
import tkinter as tk
import string
import keyboard
import pyautogui as pag
import os

""" TODO: 듀얼 모니터에서 사용 가능하도록 만들기
def fullscreen(win: Tk):
    monitors = screeninfo.get_monitors()
    width = 0
    for monitor in monitors:
        width += monitor.width
        
    win.geometry()
"""


class Grid(Tk):

    def __init__(
        self,
        cell_per_pixel=10,
        toggle_key="ctrl+windows+v",
        quit_key="ctrl+windows+q",
        adjust_amount: int = 1,
        time_out: float = 0.5,
        *args,
        **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.wait_visibility(self)
        # 배경 투명하게

        self.config(bg='#add123')

        # Create a transparent window
        self.wm_attributes('-transparentcolor', '#add123')

        # 전체 화면 모드
        self.attributes("-fullscreen", True)

        self.hook = None
        self.hidden = False
        self.toggle_key = toggle_key
        self.quit_key = quit_key
        self.cell_per_pixel = cell_per_pixel
        self.cell_positions: Dict[str, Tuple[int, int]] = {}
        cols, rows = self.grid_size()
        self.cs = self.combination_size(cols, rows)

        self.adjust_offsets = [0, 0]
        self.adjsut_amount = adjust_amount
        self.adjust_map = {
            "left": (-self.adjsut_amount, 0),
            "up": (0, -self.adjsut_amount),
            "right": (self.adjsut_amount, 0),
            "down": (0, self.adjsut_amount)
        }

        self.clear_pressed()
        keyboard.add_hotkey(self.toggle_key, self.toggle,
                            suppress=True, timeout=time_out, trigger_on_release=True)
        keyboard.add_hotkey(self.quit_key, self.end_program, suppress=True,
                            timeout=time_out, trigger_on_release=True)
        self.toggle(False)

    def end_program(self):
        keyboard.unhook_all()
        keyboard.unhook_all_hotkeys()
        os._exit(1)

    def on_key_press(self, event: keyboard.KeyboardEvent):
        """키를 입력 받았을 때 해당되는 기능 수행"""

        x = event.name
        if self.is_combination_key(x):
            """위치 지정에 사용되는 값 중 하나이면, 저장"""
            self.add_pressed(x)

            if self.is_valid_combination(self.pressed):
                """조합이 완성 됐을 때"""
                self.on_combination()

        elif x == 'esc':
            """esc는 취소. 화면 내리기"""
            self.toggle(False)

        elif self.is_adjust_key(x):
            ax, ay = self.adjust_map[x]
            self.adjust_offsets[0] += ax
            self.adjust_offsets[1] += ay
            self.adjust_grid(ax, ay)

    def add_pressed(self, key: str):
        self.pressed.append(key)

    def is_combination_key(self, x: str) -> bool:
        return x in string.ascii_lowercase

    def is_adjust_key(self, x: str) -> bool:
        return x in self.adjust_map.keys()

    def is_valid_combination(self, x: List[str]) -> bool:
        return len(x) >= self.cs

    def adjust_grid(self, x: int, y: int):
        """Grid를 Offset만큼 움직여서 보여주기"""
        self.canvas.scan_mark(0, 0)
        self.canvas.scan_dragto(x, y, gain=1)

    def on_combination(self):
        # 화면을 먼저 내린 후 끈다.
        self.toggle()
        self.click("".join(self.pressed))
        self.clear_pressed()

    def clear_pressed(self):
        self.pressed: List[str] = []

    def add_hook(self):
        self.hook = keyboard.on_press(self.on_key_press, suppress=True)

    def remove_hook(self):
        try:
            keyboard.unhook(self.hook)
        except KeyError:
            pass

        self.hook = None

    def toggle(self, value: Optional[bool] = None):

        if value:
            self.hidden = not value

        if self.hidden:
            self.deiconify()
            self.add_hook()
        else:
            self.withdraw()
            # self.iconify()
            self.remove_hook()

        self.hidden = not self.hidden

    def click(self, cell: str):

        try:
            x, y = self.cell_positions[cell]
            pag.click(x+self.adjust_offsets[0], y+self.adjust_offsets[1])
        except KeyError:
            pass

    def raise_topmost(self):
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)

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
