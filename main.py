import tkinter as tk
import random
import time
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
from tkinter import simpledialog
import pickle
import enum

# CONSTANTS
PHYSICS_FPS = 120
MS_PER_UPDATE = 1 / PHYSICS_FPS
SPEED = 100
color_array = ['red', 'purple', 'pink', 'yellow', 'blue', 'cyan', 'magenta', 'green', 'orange']
color_array_len = len(color_array)


# TODO: create stack class


class command_types(enum.Enum):
    CUT, COPY, CUT_PASTE, COPY_PASTE = range(4)


class circle:
    def __init__(self, master_canvas, x, y, r, color, identifier, active=True):
        self.master = master_canvas
        self.x = x
        self.y = y
        self.r = r  # radius
        self.d = r + r  # diameter
        self.color = color
        self.id = identifier
        self.active = active

    def update(self, ms):
        if self.active:
            dec = - SPEED * ms
            # if out of bounds
            if self.x < - self.d:
                self.x = self.master.winfo_width()
                self.set_r(random.randint(50, 80))
            else:
                self.x += dec
            # moves circle
            self.master.coords(self.id, self.x, self.y, self.x + self.d, self.y + self.d)

    # changes r and recalculates d
    def set_r(self, new_r):
        self.r = new_r
        self.d = self.r + self.r

    def get_r(self):
        return self.r

    def clone(self):
        return circle(self.master, self.x, self.y, self.r, self.color, -1)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def set_coords(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_coords(self):
        return self.x, self.y

    def get_color(self):
        return self.color




# Pattern Command, kind of
class command:
    def __init__(self, type, circle, old_x=None, old_y=None, new_x = None, new_y = None):
        self.type = type
        self.circle = circle
        # used for paste
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y

    def __str__(self):
        if self.type is command_types.CUT_PASTE:
            return str(self.type) + ' ' + self.circle.color + " " + str(self.circle.id) + " by new coords: " + str(self.new_x)+  ", " + str(self.new_y)
        return str(self.type) + ' ' + self.circle.color + " " + str(self.circle.id)

    def get_type(self):
        return self.type

    def get_circle(self):
        return self.circle

    def get_old_coords(self):
        return self.old_x, self.old_y

    def get_new_coords(self):
        return self.new_x, self.new_y


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        # visual
        self.W = 1000
        self.H = 800

        self.title('circles')
        self.geometry(str(self.W) + 'x' + str(self.H))

        self.canvas = tk.Canvas(self, width=self.W, height=self.H, bg='white')
        self.canvas.pack()

        # Main menu
        self.top_menu = tk.Menu(self)
        self.config(menu=self.top_menu)

        # "FILE" menu
        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="New", command=self.file_new)
        self.file_menu.add_command(label="Open...", command=self.file_open)
        self.file_menu.add_command(label="Save", command=self.file_save)
        self.file_menu.add_command(label="Save as", command=self.file_save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Recent file", command=self.file_recent)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit)
        self.top_menu.add_cascade(label="File", menu=self.file_menu)

        # "ACTION" menu
        self.action_menu = tk.Menu(self, tearoff=0)
        self.action_menu.add_command(label="Start simulation", command=self.start_simulation)
        self.action_menu.add_command(label="Stop simulation", command=self.stop_simulation)
        self.top_menu.add_cascade(label="Action", menu=self.action_menu)

        # "VIEW" menu
        self.top_menu.add_command(label="View")

        # "EDIT" menu
        self.edit_menu = tk.Menu(self, tearoff=0)
        # self.edit_menu.add_command(label="Paste", command=self.edit_paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=self.edit_undo)
        self.edit_menu.add_command(label="Redo", command=self.edit_redo)
        self.top_menu.add_cascade(label="Edit", menu=self.edit_menu)

        # "HELP" menu
        self.top_menu.add_command(label="Help")

        # POP-UP menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Change color", command=self.popup_choose_color)
        self.popup_menu.add_command(label="Change radius", command=self.popup_set_radius)
        self.popup_menu.add_command(label="Copy", command=self.edit_copy)
        self.popup_menu.add_command(label="Cut", command=self.edit_cut)
        self.popup_menu.add_command(label="Exit menu", command=self.popdown)

        # poptest
        self.paste_menu = tk.Menu(self, tearoff=0)
        self.paste_menu.add_command(label="Paste", command=self.edit_paste)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.protocol("WM_DELETE_WINDOW", self.exit)

        # logic
        self.circle_array = dict()
        self.lag = 0
        self.work_status = True  # shows whether app is working
        self.simulation_status = False  # shows whether circles are moving
        self.id_of_selected_circle = None  # id of chosen circle
        self.popup_mode = False  # shows whether popup menu is present on screen
        self.opened_filename = None  # stores name of opened file, used for "FILE" - > "SAVE" option
        self.stack = []
        self.stack_len = 0
        self.stack_pointer = -1
        self.circle_clicked = False
        self.cumulative_lag = 0

        # DEBUG INFO
        print("stack pointer:", self.stack_pointer)
        for i in self.stack:
            print(i)

    # creates circles
    def init_circle_array(self, num):
        for i in range(num):
            r = random.randint(50, 80)
            x = random.randint(0, self.W - r - r)
            y = random.randint(0, self.H - r - r)
            d = r + r
            color = color_array[random.randint(0, color_array_len - 1)]
            canvas_id = self.canvas.create_oval(x, y, x + d, y + d, outline=color, fill=color)
            self.circle_array[canvas_id] = circle(
                self.canvas,
                x, y, r, color, canvas_id
            )
            # makes circles clickable
            self.canvas.tag_bind(self.circle_array[canvas_id].id, '<Button-1>', self.on_circle_click)

    def main_loop(self):
        prev_t = time.time()

        while self.work_status:
            curr_t = time.time()
            elapsed = curr_t - prev_t

            prev_t = curr_t
            self.lag += elapsed
            self.cumulative_lag = self.lag

            # lag compensation
            while self.lag >= MS_PER_UPDATE:
                if self.simulation_status:
                    self.update_method(MS_PER_UPDATE)
                self.lag -= MS_PER_UPDATE

            self.tkinter_update()

    # invoked on circle click
    def on_circle_click(self, event):
        # print("circle clicked")
        self.circle_clicked = True
        # getting id of circle
        id = event.widget.find_closest(event.x, event.y)[0]
        # if not the same circle
        if id != self.id_of_selected_circle:
            # change outline to better show, that this circle is chosen
            self.canvas.itemconfig(id, outline='black')
            # simulation stops
            self.stop_simulation()
            # popup meny pops up
            self.popup(event, id)
        else:
            self.popdown()

    def on_canvas_click(self, event):
        if not self.circle_clicked:
            # print('canvas clicked')
            print(event.x, event.y)
            if self.popup_mode:
                self.popdown()
            if self.stack_pointer > -1:
                if self.stack[self.stack_pointer].get_type() is not command_types.CUT_PASTE:
                    # display the popup menu
                    try:
                        self.paste_menu.tk_popup(event.x_root, event.y_root, 0)
                        # print(self.paste_menu.winfo_x(), self.paste_menu.winfo_y())
                    finally:
                        # Release the grab
                        self.paste_menu.grab_release()
        self.circle_clicked = False

    # updates position of every circle on canvas
    def update_method(self, ms):
        for i in self.circle_array.values():
            i.update(ms)

    # circles start moving
    def start_simulation(self):
        self.simulation_status = True

    # circles stop moving
    def stop_simulation(self):
        self.simulation_status = False

    # starts new simulation
    def file_new(self):
        self.stop_simulation()
        self.clear_canvas()  # deletes previous circles
        self.init_circle_array(2)  # creates new ones
        self.start_simulation()  # they start moving

    def file_open(self):
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        prev_t = time.time()
        self.stop_simulation()

        inp_file_name = str(filedialog.askopenfilename())

        if inp_file_name == '()' or inp_file_name == '':
            messagebox.showwarning('Warning', "File is not chosen")
        else:
            # remembers what filename was opened (for further use in "FILE" -> "SAVE" option)
            self.opened_filename = inp_file_name
            # deletes previous circles
            self.clear_canvas()
            # buffer array for circles' properties
            circle_properties = self.load_circles(inp_file_name)

            # initializing circle objects
            for i in circle_properties:
                x, y, r, color = i
                d = r + r
                id = self.canvas.create_oval(x, y, x + d, y + d, outline=color, fill=color)
                self.circle_array[id] = circle(
                    self.canvas,
                    x, y, r, color, id
                )
                # makes circles clickable
                self.canvas.tag_bind(self.circle_array[id].id, '<Button-1>', self.on_circle_click)

        # lag compensation at work
        curr_t = time.time()
        print('+', (curr_t - prev_t))
        self.lag -= (curr_t - prev_t)
        # simulation starts moving
        self.start_simulation()

    def file_save(self):
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        self.stop_simulation()
        prev_t = time.time()

        if self.opened_filename is not None:
            self.dump_circles(self.opened_filename)
        else:
            messagebox.showwarning('Warning!', "File is not chosen")

        # lag compensation at work
        curr_t = time.time()
        self.lag -= (curr_t - prev_t)
        # simulation starts moving
        self.start_simulation()

    def file_save_as(self):
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        self.stop_simulation()
        prev_t = time.time()

        save_file_name = str(filedialog.asksaveasfilename())
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

    # puts into buffer, deletes from field
    def edit_cut(self):
        if self.id_of_selected_circle is not None:
            # deletes on canvas
            self.canvas.itemconfigure(self.id_of_selected_circle, state='hidden')
            # prevents moving while "invisible" state
            self.circle_array[self.id_of_selected_circle].deactivate()

            # put command on stack
            if self.stack_len - 1 == self.stack_pointer:
                self.stack.append(command(command_types.CUT, self.circle_array[self.id_of_selected_circle]))
                self.stack_len += 1
                self.stack_pointer += 1
            else:
                self.stack_pointer += 1
                self.stack[self.stack_pointer] = command(command_types.CUT, self.circle_array[self.id_of_selected_circle])
                self.stack = self.stack[self.stack_pointer + 1]

            #print("stack pointer:", self.stack_pointer)
            #for i in self.stack:
                #print(i)

        else:
            messagebox.showwarning('Warning!', 'Circle is not chosen!')
        self.popdown()

    # only puts to buffer
    def edit_copy(self):
        if self.id_of_selected_circle is not None:
            # put command on stack
            if self.stack_len - 1 == self.stack_pointer:
                self.stack.append(command(command_types.COPY, self.circle_array[self.id_of_selected_circle]))
                self.stack_len += 1
                self.stack_pointer += 1
            else:
                self.stack_pointer += 1
                self.stack[self.stack_pointer] = command(
                    command_types.COPY,
                    self.circle_array[self.id_of_selected_circle]
                )
                self.stack = self.stack[self.stack_pointer + 1]
        else:
            messagebox.showwarning('Warning!', 'Circle is not chosen!')

        self.popdown()

    #   takes from buffer, puts on field
    def edit_paste(self):
        previous_command = self.stack[self.stack_pointer]
        # does not create new entity
        if previous_command.get_type() is command_types.CUT:
            old_x = previous_command.circle.x
            old_y = previous_command.circle.y
            previous_command.circle.x = self.paste_menu.winfo_x() - self.winfo_x()
            previous_command.circle.y = self.paste_menu.winfo_y() - self.winfo_y()
            previous_command.circle.activate()
            self.canvas.itemconfigure(previous_command.circle.id, state='normal')

            if self.stack_len - 1 == self.stack_pointer:
                self.stack.append(
                    command(
                        command_types.CUT_PASTE,
                        self.circle_array[previous_command.circle.id],
                        old_x, old_y,
                        self.paste_menu.winfo_x() - self.winfo_x(), self.paste_menu.winfo_y() - self.winfo_y()
                    )
                )
                self.stack_len += 1
                self.stack_pointer += 1
            else:
                self.stack_pointer += 1
                self.stack[self.stack_pointer] = command(
                    command_types.CUT_PASTE,
                    self.circle_array[previous_command.circle.id],
                    old_x, old_y, self.paste_menu.winfo_x() - self.winfo_x(), self.paste_menu.winfo_y() - self.winfo_y()
                )
                self.stack = self.stack[self.stack_pointer + 1]
        # creation of new entity happens
        else:
            r = previous_command.get_circle().get_r()
            new_x = self.paste_menu.winfo_x() - self.winfo_x()
            new_y = self.paste_menu.winfo_y() - self.winfo_y()
            d = r + r
            color = previous_command.get_circle().get_color()
            canvas_id = self.canvas.create_oval(new_x, new_y, new_x + d, new_y + d, outline=color, fill=color)
            self.circle_array[canvas_id] = circle(
                self.canvas,
                new_x, new_y, r, color, canvas_id
            )
            # makes circles clickable
            self.canvas.tag_bind(canvas_id, '<Button-1>', self.on_circle_click)

            if self.stack_len - 1 == self.stack_pointer:
                self.stack.append(command(command_types.COPY_PASTE, self.circle_array[canvas_id]))
                self.stack_len += 1
                self.stack_pointer += 1
            else:
                self.stack_pointer += 1
                self.stack[self.stack_pointer] = command(command_types.COPY_PASTE, self.circle_array[canvas_id])
                self.stack = self.stack[self.stack_pointer + 1]

        #print("stack pointer:", self.stack_pointer)
        #for i in self.stack:
            #print(i)

        self.paste_menu.unpost()

    def edit_undo(self):
        if self.stack_len > 0 and self.stack_pointer > -1:
            if self.stack[self.stack_pointer].get_type() is command_types.CUT:
                self.stack[self.stack_pointer].get_circle().activate()
                self.canvas.itemconfigure(self.stack[self.stack_pointer].get_circle().id, state='normal')
                self.stack_pointer -= 1
            elif self.stack[self.stack_pointer].get_type() is command_types.CUT_PASTE:
                self.stack[self.stack_pointer].get_circle().set_coords(*self.stack[self.stack_pointer].get_old_coords())
                self.stack[self.stack_pointer].get_circle().deactivate()
                self.canvas.itemconfigure(self.stack[self.stack_pointer].get_circle().id, state='hidden')
                self.stack_pointer -= 1
            elif self.stack[self.stack_pointer].get_type() is command_types.COPY:
                self.stack_pointer -= 1
                self.edit_undo()
            elif self.stack[self.stack_pointer].get_type() is command_types.COPY_PASTE:
                self.canvas.delete(self.stack[self.stack_pointer].get_circle().id)
                del self.circle_array[self.stack[self.stack_pointer].get_circle().id]
                self.stack_pointer -= 1

            #print("stack pointer:", self.stack_pointer)
            #for i in self.stack:
                #print(i)

    def edit_redo(self):
        if self.stack_pointer < self.stack_len - 1:
            self.stack_pointer += 1
            if self.stack[self.stack_pointer].get_type() is command_types.CUT:
                # deletes on canvas
                self.canvas.itemconfigure(self.stack[self.stack_pointer].get_circle().id, state='hidden')
                # prevents moving while "invisible" state
                self.circle_array[self.stack[self.stack_pointer].get_circle().id].deactivate()
            elif self.stack[self.stack_pointer].get_type() is command_types.CUT_PASTE:
                self.stack[self.stack_pointer].get_circle().set_coords(*self.stack[self.stack_pointer].get_new_coords())
                self.stack[self.stack_pointer].get_circle().activate()
                self.canvas.itemconfigure(self.stack[self.stack_pointer].get_circle().id, state='normal')
            elif self.stack[self.stack_pointer].get_type() is command_types.COPY:
                self.edit_redo()
            elif self.stack[self.stack_pointer].get_type() is command_types.COPY_PASTE:
                r = self.stack[self.stack_pointer].get_circle().get_r()
                new_x, new_y = self.stack[self.stack_pointer].get_circle().get_coords()
                d = r + r
                color = self.stack[self.stack_pointer].get_circle().get_color()
                canvas_id = self.canvas.create_oval(new_x, new_y, new_x + d, new_y + d, outline=color, fill=color)
                self.circle_array[canvas_id] = circle(
                    self.canvas,
                    new_x, new_y, r, color, canvas_id
                )
                # makes circles clickable
                self.canvas.tag_bind(canvas_id, '<Button-1>', self.on_circle_click)

                self.stack[self.stack_pointer].get_circle().id = canvas_id

            #print("stack pointer:", self.stack_pointer)
            #for i in self.stack:
                #print(i)

    def exit(self):
        self.work_status = False

    # because .mainloop() is not used, I have to create custom cycle
    '''
        root.mainloop() 

        should be equivalent to

        while True:
            root.update()
            root.update_idletasks()

        at least I believe so
    '''

    def tkinter_update(self):
        self.update()
        self.update_idletasks()

    def popup_choose_color(self):
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        self.stop_simulation()
        prev_t = time.time()

        color = colorchooser.askcolor()
        if color[1] is not None:
            self.circle_array[self.id_of_selected_circle].color = color[1]
            self.canvas.itemconfig(self.id_of_selected_circle, fill=color[1])

        # popup mode is turned off
        self.popup_mode = False
        # circle outline returns to its own color
        self.canvas.itemconfig(self.id_of_selected_circle,
                               outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill'))
        # no circle is chosen
        self.id_of_selected_circle = None

        # lag compensation at work
        curr_t = time.time()
        self.lag -= (curr_t - prev_t)
        self.start_simulation()

    def popup_set_radius(self):
        # these timestamps are needed to compensate time during which circles are not moving,
        # but while they stay still lag is growing
        self.stop_simulation()
        prev_t = time.time()

        r = simpledialog.askinteger(
            "Radius", "Input number in range [50; 80]",
            parent=self,
            minvalue=50, maxvalue=80
        )

        if r is not None:
            self.circle_array[self.id_of_selected_circle].set_r(r)

        # popup mode is turned off
        self.popup_mode = False
        # circle outline returns to its own color
        self.canvas.itemconfig(self.id_of_selected_circle,
                               outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill'))
        # no circle is chosen
        self.id_of_selected_circle = None

        # lag compensation at work
        curr_t = time.time()
        self.lag -= (curr_t - prev_t)
        self.start_simulation()

    def popup(self, event, id):
        # print('up')
        # if circle clicked at while popup menu is still present
        if self.popup_mode:
            # previous circle outline returns to its own color
            self.canvas.itemconfig(self.id_of_selected_circle,
                                   outline=self.canvas.itemcget(self.id_of_selected_circle, 'fill'))
        else:
            # if popup menu called from hidden state
            self.popup_mode = True

        # id of circle being clicked
        self.id_of_selected_circle = id
        # show popup menu
        self.popup_menu.post(event.x_root, event.y_root)
        self.popup_menu.focus_set()

    # hides popup menu
    def popdown(self, event=None):
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
        self.start_simulation()

    # clears canvas
    def clear_canvas(self):
        # deletes all circles on canvas
        self.canvas.delete('all')
        # deletes all circle objects
        self.circle_array = dict()

    def load_circles(self, filename):
        try:
            file_desc = open(filename, 'rb')
            object = pickle.load(file_desc)
            file_desc.close()
            return object
        except Exception as e:
            print(e)
            exit()

    def dump_circles(self, filename):
        try:
            file_desc = open(filename, 'wb')
            circle_properties = []
            for i in self.circle_array.values():
                circle_properties.append(
                    [
                        i.x,
                        i.y,
                        i.r,
                        i.color
                    ]
                )
            pickle.dump(circle_properties, file_desc)
            file_desc.close()
        except Exception as e:
            print(e)
            exit()


win = main_window()
# win.init_circle_array(25)
win.main_loop()
