import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
from tkinter import simpledialog

import random
import time
import pickle

from typing import Optional

# My files
from Command import Command_types, Command
from Consts import *
from Stack import Stack
from Circle import Circle


# Main window
class Main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        ### VISUAL PART

        # WIndow parameters
        self.W : int = 1600
        self.H : int = 1000
        self.title('circles')
        self.geometry(str(self.W) + 'x' + str(self.H))

        # Canvas
        self.canvas : tk.Canvas = tk.Canvas(self, width=self.W, height=self.H, bg='white')
        self.canvas.pack()

        # Main menu
        self.top_menu : tk.Menu = tk.Menu(self)
        self.config(menu=self.top_menu)

        # "FILE" menu
        self.file_menu : tk.Menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="New", command=self.file_new)
        self.file_menu.add_command(label="Open...", command=self.file_open)
        self.file_menu.add_command(label="Save", command=self.file_save)
        self.file_menu.add_command(label="Save as", command=self.file_save_as)
        #self.file_menu.add_separator()
        #self.file_menu.add_command(label="Recent files", command=self.file_recent)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit)
        self.top_menu.add_cascade(label="File", menu=self.file_menu)

        # "ACTION" menu
        self.action_menu : tk.Menu = tk.Menu(self, tearoff=0)
        self.action_menu.add_command(label="Start simulation", command=self.start_simulation)
        self.action_menu.add_command(label="Stop simulation", command=self.stop_simulation)
        self.top_menu.add_cascade(label="Action", menu=self.action_menu)

        # "VIEW" menu
        self.top_menu.add_command(label="View")

        # "EDIT" menu
        self.edit_menu : tk.Menu = tk.Menu(self, tearoff=0)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=self.edit_undo)
        self.edit_menu.add_command(label="Redo", command=self.edit_redo)
        self.top_menu.add_cascade(label="Edit", menu=self.edit_menu)

        # "HELP" menu
        self.top_menu.add_command(label="Help")

        # POP-UP menu
        self.popup_menu : tk.Menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Change color", command=self.popup_choose_color)
        self.popup_menu.add_command(label="Change radius", command=self.popup_set_radius)
        self.popup_menu.add_command(label="Copy", command=self.edit_copy)
        self.popup_menu.add_command(label="Cut", command=self.edit_cut)
        self.popup_menu.add_command(label="Exit menu", command=self.popdown)

        # paste menu
        self.paste_menu : tk.Menu = tk.Menu(self, tearoff=0)
        self.paste_menu.add_command(label="Paste", command=self.edit_paste)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Prevents errors from pressing 'x' button
        self.protocol("WM_DELETE_WINDOW", self.exit)

        # logic
        self.circle_array : dict[int, Circle] = dict() # Circles are stored here
        self.lag : float = 0    # Used for Game Cycle pattern
        self.work_status : bool = True  # shows whether app is working
        self.simulation_status : bool = False  # shows whether all circles are moving
        self.id_of_selected_circle : int = -1  # id of chosen circle
        self.popup_mode : bool = False  # shows whether popup menu is present on screen
        self.opened_filename : bool = None  # stores name of opened file, used for "FILE" - > "SAVE" option
        self.stack : Stack = Stack()
        self.circle_clicked : bool = False

        # DEBUG INFO
        #print(self.stack)

    # creates circles
    def init_circle_array(self, num: int) -> None:
        cell_width : int = int(self.W / 6)
        cell_height : int = int (self.H / 5)
        for i in range(6):
            for j in range(5):

                r: float = random.randint(50, 80)
                d: float = r + r
                x: float = random.randint(i * cell_width, (i + 1) * cell_width - d)
                y: float = random.randint(j * cell_height, (j+ 1) * cell_height - d)
                #self.canvas.create_line(i * cell_width, j * cell_height, i * cell_width,  j * cell_height + d)
                #self.canvas.create_line(i * cell_width, j * cell_height, i * cell_width + d, j * cell_height + d)

                color: str = color_array[random.randint(0, color_array_len - 1)]
                # creates circle on Canvas
                canvas_id: int = self.canvas.create_oval(x, y, x + d, y + d, outline=color, fill=color)
                # adds circles to be processed in main cycle
                self.circle_array[canvas_id] = Circle(
                    self.canvas,
                    x, y, r, color, canvas_id
                )
                # makes circles clickable
                self.canvas.tag_bind(self.circle_array[canvas_id].get_id(), '<Button-1>', self.on_circle_click)
        '''
        for i in range(num):
            # Circle parameters
            r: float = random.randint(50, 80)
            x: float = random.randint(0, self.W - r - r)
            y: float = random.randint(0, self.H - r - r)
            d: float = r + r
            color: str = color_array[random.randint(0, color_array_len - 1)]
            # creates circle on Canvas
            canvas_id: int = self.canvas.create_oval(x, y, x + d, y + d, outline=color, fill=color)
            # adds circles to be processed in main cycle
            self.circle_array[canvas_id] = Circle(
                self.canvas,
                x, y, r, color, canvas_id
            )
            # makes circles clickable
            self.canvas.tag_bind(self.circle_array[canvas_id].get_id(), '<Button-1>', self.on_circle_click)
        '''
    def main_loop(self) -> None:
        prev_t: float = time.time()

        while self.work_status:
            # calculates lag
            curr_t: float = time.time()
            elapsed: float  = curr_t - prev_t

            prev_t: float = curr_t
            self.lag += elapsed

            # if lag is more than MS_PER_UPDATE skips rendering (scource: Game programming patterns)
            while self.lag >= MS_PER_UPDATE:
                if self.simulation_status:
                    self.update_method(MS_PER_UPDATE)
                self.lag -= MS_PER_UPDATE

            # updates window
            self.tkinter_update()

    # handles on circle click
    def on_circle_click(self, event: tk.Event) -> None:
        if not self.simulation_status:
            # prevents on_canvas_click from working
            self.circle_clicked = True
            # getting id of circle
            id: int = event.widget.find_closest(event.x, event.y)[0]
            # if not the same circle
            if id != self.id_of_selected_circle:
                # change outline to better show, that this circle is chosen
                self.canvas.itemconfig(id, outline='black')
                # popup meny pops up
                self.popup(event, id)
            else:
                self.popdown()

    # handles on canvas click
    def on_canvas_click(self, event: tk.Event) -> None:
        if not self.simulation_status:
            if not self.circle_clicked:
                # closes menu if opened
                if self.popup_mode:
                    self.popdown()
                if not self.stack.is_empty():
                    if self.stack.curr().get_type() is not Command_types.CUT_PASTE:
                        # display the popup menu
                        try:
                            self.paste_menu.tk_popup(event.x_root, event.y_root, 0)
                            # print(self.paste_menu.winfo_x(), self.paste_menu.winfo_y())
                        finally:
                            # Release the grab
                            self.paste_menu.grab_release()
            self.circle_clicked = False

    # updates position of every circle on canvas
    def update_method(self, ms: float) -> None:
        for i in self.circle_array.values():
            i.update(ms)

    # circles start moving
    def start_simulation(self) -> None:
        self.simulation_status = True

    # circles stop moving
    def stop_simulation(self) -> None:
        self.simulation_status = False

    # starts new simulation
    def file_new(self) -> None:
        self.stop_simulation()      # stops simulation
        self.clear_canvas()         # deletes previous circles
        self.init_circle_array(30)   # creates new ones
        #self.start_simulation()     # they start moving
        self.stack.clear()

    def file_open(self) -> None:
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        prev_t: float = time.time()
        self.stop_simulation()

        # ask filename
        inp_file_name: str = str(filedialog.askopenfilename())

        if inp_file_name == '()' or inp_file_name == '':
            messagebox.showwarning('Warning', "File is not chosen")
        else:
            # remembers what filename was opened (for further use in "FILE" -> "SAVE" option)
            self.opened_filename = inp_file_name
            # deletes previous circles
            self.clear_canvas()
            # buffer array for circles' properties
            circle_properties: list[float, float, float, str] = self.load_circles(inp_file_name)

            # initializing circle objects
            for i in circle_properties:
                x, y, r, color = i
                d: float = r + r
                id: int = self.canvas.create_oval(x, y, x + d, y + d, outline=color, fill=color)
                self.circle_array[id] = Circle(
                    self.canvas,
                    x, y, r, color, id
                )
                # makes circles clickable
                self.canvas.tag_bind(self.circle_array[id].get_id(), '<Button-1>', self.on_circle_click)

        # lag compensation
        curr_t: float = time.time()
        self.lag -= (curr_t - prev_t)
        # simulation starts moving
        self.stack.clear()
        self.start_simulation()

    # saves circle parameters to a file
    def file_save(self) -> None:

        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        self.stop_simulation()
        prev_t: float = time.time()

        # checks if file was opened, if file was not opened, should use Save As
        if self.opened_filename is not None:
            self.dump_circles(self.opened_filename)
        else:
            messagebox.showwarning('Warning!', "File is not chosen")

        # lag compensation
        curr_t: float = time.time()
        self.lag -= (curr_t - prev_t)
        # simulation starts moving
        self.start_simulation()

    # saves circles to a new file
    def file_save_as(self) -> None:
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        self.stop_simulation()
        prev_t: float = time.time()

        # new file name
        save_file_name: str = str(filedialog.asksaveasfilename())
        if save_file_name == '()' or save_file_name == '':
            messagebox.showwarning('Warning!', "File is not chosen")
            return

        # dumps circle properties by pickle into file
        self.dump_circles(save_file_name)

        # lag compensation at work
        curr_t = time.time()
        self.lag -= (curr_t - prev_t)
        self.start_simulation()

    def file_recent(self):
        pass

    # handles 'popup_menu' -> 'cut'
    def edit_cut(self) -> None:
        if self.id_of_selected_circle is not None:
            # put command on stack
            self.stack.put(Command(Command_types.CUT, self.circle_array[self.id_of_selected_circle]))
            # execute command
            self.execute()
        else:
            messagebox.showwarning('Warning!', 'Circle is not chosen!')
        self.popdown()

    # handles 'popup_menu' -> 'copy'
    def edit_copy(self) -> None:
        if self.id_of_selected_circle is not None:
            # put command on stack
            self.stack.put(Command(Command_types.COPY, self.circle_array[self.id_of_selected_circle]))
            #self.execute()
        else:
            messagebox.showwarning('Warning!', 'Circle is not chosen!')
        self.popdown()

    #  handles 'paste_menu' -> paste
    def edit_paste(self) -> None:
        previous_command = self.stack.curr()
        if previous_command.get_type() is Command_types.CUT:
            # saving new and old coordinates of the circle
            old_x, old_y = previous_command.get_circle().get_coords()
            new_x: float = self.paste_menu.winfo_x() - self.winfo_x()
            new_y: float = self.paste_menu.winfo_y() - self.winfo_y()

            self.stack.put(
                Command(
                    Command_types.CUT_PASTE,
                    self.circle_array[previous_command.get_circle().get_id()],
                    old_x, old_y,
                    new_x, new_y
                )
            )
        else:
            # saves only new coordiantes
            new_x = self.paste_menu.winfo_x() - self.winfo_x()
            new_y = self.paste_menu.winfo_y() - self.winfo_y()

            self.stack.put(
                Command(Command_types.COPY_PASTE, self.circle_array[previous_command.get_circle().get_id()],
                        new_x=new_x, new_y=new_y
                )
            )
        self.execute()
        self.paste_menu.unpost()

    # handles 'edit_menu' -> 'undo'
    def edit_undo(self) -> None:
        # if stack contains commands
        if self.stack.can_go_down():
            if self.stack.curr().get_type() is not Command_types.COPY:
                self.rollback()
                self.stack.go_down()
            else:
                # because copy cannot be executed
                if self.stack.can_go_down():
                    self.stack.go_down()
                    self.edit_undo()

    # handles 'edit_menu' -> redo
    def edit_redo(self) -> None:
        #print(self.stack)
        if self.stack.can_go_up():
            self.stack.go_up()
            if self.stack.curr().get_type() is not Command_types.COPY:
                self.execute()
            #
            else:
                self.edit_redo()

    # executes current command on stack
    def execute(self) -> None:
        print('execution')
        if self.stack.curr().get_type() is Command_types.CUT:
            # deletes on canvas
            self.canvas.itemconfigure(self.stack.curr().get_circle().get_id(), state='hidden')
            # prevents moving while "invisible" state
            self.circle_array[self.stack.curr().get_circle().get_id()].deactivate()
        elif self.stack.curr().get_type() is Command_types.CUT_PASTE:
            # sets new coordinates
            self.stack.curr().get_circle().set_coords(*self.stack.curr().get_new_coords())
            # makes circle movable
            self.stack.curr().get_circle().activate()
            # shows circle on canvas
            self.canvas.itemconfigure(self.stack.curr().get_circle().get_id(), state='normal')
            self.stack.curr().get_circle().update(0)
        #elif self.stack.curr().get_type() is Command_types.COPY:
            #pass
            # COPY cannot be executed
        elif self.stack.curr().get_type() is Command_types.COPY_PASTE:
            # getting pararmeters for circle
            r: float = self.stack.curr().get_circle().get_r()
            new_x, new_y = self.stack.curr().get_new_coords()
            d: float = r + r
            color: str = self.stack.curr().get_circle().get_color()
            canvas_id: int = self.canvas.create_oval(new_x, new_y, new_x + d, new_y + d, outline=color, fill=color)
            self.circle_array[canvas_id] = Circle(
                self.canvas,
                new_x, new_y, r, color, canvas_id
            )
            # when we put ptototype circle on stack, and after creation of new (but with the same parameters except id)
            # we replace prototype with new one
            self.stack.curr().set_circle(self.circle_array[canvas_id])
            self.stack.curr().get_circle().set_id(canvas_id)
            # makes circle clickable
            self.canvas.tag_bind(canvas_id, '<Button-1>', self.on_circle_click)

    # rolls back current command on stack
    def rollback(self) -> None:
        if self.stack.curr().get_type() is Command_types.CUT:
            self.stack.curr().get_circle().activate()
            self.canvas.itemconfigure(self.stack.curr().get_circle().get_id(), state='normal')
        elif self.stack.curr().get_type() is Command_types.CUT_PASTE:
            self.stack.curr().get_circle().set_coords(*self.stack.curr().get_old_coords())
            self.stack.curr().get_circle().deactivate()
            self.canvas.itemconfigure(self.stack.curr().get_circle().get_id(), state='hidden')
        #elif self.stack.curr().get_type() is Command_types.COPY:
            # COPY cannot be executed
        elif self.stack.curr().get_type() is Command_types.COPY_PASTE:
            self.canvas.delete(self.stack.curr().get_circle().get_id())
            del self.circle_array[self.stack.curr().get_circle().get_id()]

    # stops main cycle
    def exit(self) -> None:
        self.work_status = False

    # because .mainloop() is not used, I have to create custom cycle
    #
    # root.mainloop()
    #
    # should be equivalent to
    #
    # while True:
    #   root.update()
    #   root.update_idletasks()
    #
    # at least I believe so

    # updates main window instead of .mainloop()
    def tkinter_update(self) -> None:
        self.update()
        self.update_idletasks()

    # handles 'popup_menu' -> 'change color'
    def popup_choose_color(self) -> None:

        # ask for color
        color: str = colorchooser.askcolor()
        # sets color

        if color[1] is not None:
            self.circle_array[self.id_of_selected_circle].set_color(color[1])
            self.canvas.itemconfig(self.id_of_selected_circle, fill=color[1])
            self.circle_array[self.id_of_selected_circle].update(0)

        # popup mode is turned off
        self.popup_mode = False
        # circle outline returns to its own color
        self.canvas.itemconfig(
            self.id_of_selected_circle,
            outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill')
        )
        # no circle is chosen
        self.id_of_selected_circle = None


    # handles 'popup_menu' -> 'change radius'
    def popup_set_radius(self):

        r = simpledialog.askinteger(
            "Radius", "Input number in range [50; 80]",
            parent=self,
            minvalue=50, maxvalue=80, initialvalue=self.circle_array[self.id_of_selected_circle].get_r()
        )

        if r is not None:
            self.circle_array[self.id_of_selected_circle].set_r(r)
            self.circle_array[self.id_of_selected_circle].update(0)

        # popup mode is turned off
        self.popup_mode = False
        # circle outline returns to its own color
        self.canvas.itemconfig(self.id_of_selected_circle,
                               outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill'))
        # no circle is chosen
        self.id_of_selected_circle = None


    def popup(self, event, id) -> None:
        # if circle clicked at while popup menu is still present
        if self.popup_mode:
            # previous circle outline returns to its own color
            self.canvas.itemconfig(self.id_of_selected_circle,
                outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill')
            )
        else:
            # if popup menu called from hidden state
            self.popup_mode = True

        # id of circle being clicked
        self.id_of_selected_circle = id
        # show popup menu
        self.popup_menu.post(event.x_root, event.y_root)
        self.popup_menu.focus_set()

    # hides popup menu
    def popdown(self, event: Optional[tk.Event] = None) ->None:
        # print('down')
        # popup mode is turned off
        self.popup_mode = False
        # circle outline returns to its own color
        self.canvas.itemconfig(self.id_of_selected_circle,
                               outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill'))
        # hide menu
        self.popup_menu.unpost()
        # no circle is chosen
        self.id_of_selected_circle = None
        # simulation starts
       # self.start_simulation()

    # clears canvas
    def clear_canvas(self) -> None:
        # deletes all circles on canvas
        self.canvas.delete('all')
        # deletes all circle objects
        self.circle_array = dict()

    def load_circles(self, filename) -> None:
        try:
            file_desc = open(filename, 'rb')
            object = pickle.load(file_desc)
            file_desc.close()
            return object
        except Exception as e:
            print(e)
            exit()

    def dump_circles(self, filename) -> None:
        try:
            file_desc = open(filename, 'wb')
            circle_properties = []
            for i in self.circle_array.values():
                circle_properties.append(
                    [
                        i.get_x(),
                        i.get_y(),
                        i.get_r(),
                        i.get_color()
                    ]
                )
            pickle.dump(circle_properties, file_desc)
            file_desc.close()
        except Exception as e:
            print(e)
            exit()




win = Main_window()
win.main_loop()
