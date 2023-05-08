from Command import Command, Command_types


class Stack:
    def __init__(self):
        self.__stack: list[Command] = []
        self.__stack_len: int = 0
        self.__stack_pointer: int = -1

    def put(self, command: Command) -> None:
        # put command on stack
        if self.__stack_len - 1 == self.__stack_pointer:
            self.__stack.append(command)
            self.__stack_len += 1
            self.__stack_pointer += 1
        else:
            self.__stack_pointer += 1
            self.__stack[self.__stack_pointer] = command
            self.__stack = self.__stack[self.__stack_pointer + 1]

    def curr(self) -> Command:
        if self.__stack_pointer > -1:
            return self.__stack[self.__stack_pointer]
        return Command(Command_types.NO_COMMAND, None)

    # index increases
    def go_up(self) -> None:
        if self.__stack_pointer < self.__stack_len - 1:
            self.__stack_pointer += 1

    def go_down(self) -> None:
        if self.__stack_len > 0 and self.__stack_pointer > -1:
            self.__stack_pointer -= 1

    def can_go_up(self) -> bool:
        if self.__stack_pointer < self.__stack_len - 1:
            return True
        return False

    def can_go_down(self) -> bool:
        if self.__stack_len > 0 and self.__stack_pointer > -1:
            return True
        return False

    def is_empty(self) -> bool:
        if self.__stack_pointer > -1:
            return False
        return True

    def __str__(self) -> str:
        return 'stack pointer: ' + str(self.__stack_pointer) + '\n' + '\n'.join(list(map(lambda x: x.__str__(), self.__stack)))
