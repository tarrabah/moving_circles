import enum
from Circle import Circle
from typing import Optional


class Command_types(enum.Enum):
    CUT, COPY, CUT_PASTE, COPY_PASTE, NO_COMMAND = range(5)


# Pattern Command, kind of
class Command:
    def __init__(self, c_type: Command_types, circle: Optional[Circle], old_x: float = 0, old_y: float = 0, new_x: float = 0,
                 new_y: float = 0):
        self.__type = c_type
        self.__circle = circle
        # used for paste
        self.__old_x = old_x
        self.__old_y = old_y
        self.__new_x = new_x
        self.__new_y = new_y

    def __str__(self) -> str:
        if self.__type is Command_types.CUT_PASTE:
            return str(self.__type) + ' ' + self.__circle.get_color() + " " + str(self.__circle.get_id()) + " by new coords: " + str(
                self.__new_x) + ", " + str(self.__new_y)
        return str(self.__type) + ' ' + self.__circle.get_color() + " " + str(self.__circle.get_id())

    def get_type(self) -> Command_types:
        return self.__type

    def get_circle(self) -> Circle:
        return self.__circle

    def set_circle(self, new_circle):
        self.__circle = new_circle

    def get_old_coords(self) -> tuple[float, float]:
        return self.__old_x, self.__old_y

    def get_new_coords(self) -> tuple[float, float]:
        return self.__new_x, self.__new_y
