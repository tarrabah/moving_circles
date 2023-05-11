import tkinter as tk
import random
from Consts import *


class Circle:
    def __init__(self, master_canvas: tk.Canvas, x: float, y: float, r: float, color: str, identifier: int,
                 active=True):
        # private members
        self.__master: tk.Canvas = master_canvas
        self.__x: float = x
        self.__y: float = y
        self.__r: float = r  # radius
        self.__d: float = r + r  # diameter
        self.__color: str = color
        self.__id: int = identifier
        self.__active: bool = active

    def update(self, ms: float) -> None:
        if self.__active:
            dec: float = - SPEED * ms
            # if out of bounds
            if self.__x < - self.__d:
                self.__x = self.__master.winfo_width()
                self.set_r(random.randint(50, 80))
            else:
                self.__x += dec
            # moves circle
            self.__master.coords(self.__id, self.__x, self.__y, self.__x + self.__d, self.__y + self.__d)

    # changes r and recalculates d
    def set_r(self, new_r: float) -> None:
        self.__r = new_r
        self.__d = self.__r + self.__r

    def get_r(self) -> float:
        return self.__r

    def activate(self) -> None:
        self.__active = True

    def deactivate(self) -> None:
        self.__active = False

    def set_coords(self, new_x: float, new_y: float) -> None:
        self.__x = new_x
        self.__y = new_y

    def get_coords(self) -> tuple[float, float]:
        return self.__x, self.__y

    def get_x(self) -> float:
        return self.__x

    def get_y(self) -> float:
        return self.__y

    def get_color(self) -> str:
        return self.__color

    def set_color(self, new_color) -> None:
        self.__color = new_color

    def get_id(self) -> int:
        return self.__id

    def set_id(self, new_id: int) -> None:
        self.__id = new_id