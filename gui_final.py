import re
import time
import datetime
import threading
from tkinter import *
from tkinter import ttk
from copy import copy
from tkinter import messagebox
from cybercafe_db import User, Staff, Machine
from PIL import ImageTk, Image, ImageDraw, ImageFont
from ttkthemes import themed_tk as tk


sec_deposit = {"0 months": "20", "1 month": "2000", "3 months": "5000", "6 months": "9500", "12 months": "18000"}


# NOTE: Utility Classes
class EmptyFieldError(Exception):
    def __init__(self, msg, key=None):
        self.message = msg
        self.key = key
        super().__init__()


class MatchNotFoundError(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__()


class InvalidLengthError(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__()


class InvalidFormatError(Exception):
    def __init__(self, msg, key):
        self.message = msg
        self.key = key
        super().__init__()


class EntryWithPlaceholder(ttk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_fg_color = "black"

        self.bind("<Button-1>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color

    def foc_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, END)
            self['foreground'] = self.default_fg_color

    def foc_out(self, event):
        if not self.get():
            self.put_placeholder()


class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.text = ""

    def showtip(self, text):
        """Display text in tooltip window"""
        self.text = text
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 42
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT, background="#ffffe0",
                      relief=SOLID, borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class TogglePasswordButton(ttk.Button):

    def __init__(self, mode, *args, **kwargs):
        ttk.Button.__init__(self, *args, **kwargs)
        if mode == "show":
            src1 = "images/open_eye.png"
            photo1 = PhotoImage(file=src1)
            self['image'] = photo1
            self.image = photo1
            create_tool_tip(self, "Show Password")
        if mode == "hide":
            src2 = "images/closed_eye.png"
            photo2 = PhotoImage(file=src2)
            self['image'] = photo2
            self.image = photo2
            create_tool_tip(self, "Hide Password")

    def toggle_passwd(self, entry, buttons, **kwargs):
        if entry["show"] == "*":
            entry.config(show="")
            self.grid_remove()
            buttons[1].grid(kwargs)
            buttons[1]['command'] = lambda: buttons[1].toggle_passwd(entry, buttons, **kwargs)
        else:
            entry.config(show="*")
            self.grid_remove()
            buttons[0].grid(kwargs)
            buttons[0]['command'] = lambda: buttons[0].toggle_passwd(entry, buttons, **kwargs)


# NOTE: Auxiliary Functions
def create_tool_tip(widg, text):
    tool_tip = ToolTip(widg)

    def enter(event):
        tool_tip.showtip(text)

    def leave(event):
        tool_tip.hidetip()

    widg.bind('<Enter>', enter)
    widg.bind('<Leave>', leave)


def get_object(nb):
    obj_dict = {"User": user, "Staff": staff, "Machine": machine}
    obj_id = nb.tab(nb.select())['text'].split(' ')[0]
    return obj_dict[obj_id]


def create_tab(nb, heading, lbl_id, curr_frame):

    obj_dict = {"User": user, "Staff": staff, "Machine": machine}
    obj_id = heading.split(' ')[0]
    obj = obj_dict[obj_id]

    frame = ttk.Frame(nb)
    frame.pack(fill=BOTH, expand=1, anchor=CENTER)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill=BOTH, expand=1)

    l1 = ttk.Label(header_frame, text=heading, font="Helvetica 26 bold italic")

    photo1 = ImageTk.PhotoImage(Image.open("images/logout_icon.png"))
    back_btn = ttk.Button(header_frame, image=photo1, command=lambda: back(curr_frame, nb, True))
    back_btn.image = photo1
    create_tool_tip(back_btn, "Logout")

    l1.grid(row=0, column=0, padx=(195,5), pady=5)

    if type(obj) == Machine:
        back_btn.grid(row=0, column=1, padx=(60,5), pady=5)
    else:
        back_btn.grid(row=0, column=1, padx=(120,5), pady=5)

    # top frame
    top_frame = ttk.Frame(frame)
    top_frame.pack(anchor=CENTER)
    id_lbl = ttk.Label(top_frame, text=lbl_id)
    id_lbl.grid(row=0, column=0, padx=10, pady=10, sticky=E)

    e1 = ttk.Entry(top_frame, width=30)
    e1.grid(row=0, column=1, padx=10, pady=10, sticky=W)

    photo = ImageTk.PhotoImage(Image.open("images/search2.png"))
    search_button = ttk.Button(top_frame, image=photo)
    search_button.grid(row=0, column=2, padx=2, ipadx=0, ipady=0)
    search_button.image = photo
    create_tool_tip(search_button, "Search")

    # middle frame
    mid_frame = ttk.Frame(frame)
    mid_frame.pack(anchor=CENTER)

    f1 = ttk.Frame(mid_frame)
    f1.pack(fill=BOTH, expand=1)

    columns = ()
    if type(obj) == User:
        columns = ("Email Id", "Full Name", "Contact No.", "Password", "Reg. Date", "Reg. Day",
                   "Membership Pd.", "Security", "Balance")
    if type(obj) == Staff:
        columns = ("Email Id", "Full Name", "Contact No.", "Password", "Reg. Date", "Reg. Day",
                   "Salary")
    if type(obj) == Machine:
        columns = ("Model No.", "Item", "Brand", "Price", "Warranty", "Buy Date", "Buy Day")

    tree1 = ttk.Treeview(f1)
    tree1['columns'] = columns

    # configure email entry box and search button
    search_button.config(command=lambda: search(nb, tree1, e1))
    e1.bind('<Return>', lambda event: search(nb, tree1, e1))

    # styling treeview
    style = ttk.Style(tree1)
    style.configure("Treeview",
                    background="#EFEFEF",
                    foreground="black",
                    rowheight=20,
                    fieldbackground="#EFEFEF"
                    )
    style.map("Treeview",
              background=[('selected', 'pink')]
              )
    tree1.tag_configure("oddrow", background="#EFEFEF")
    tree1.tag_configure("evenrow", background="light yellow")

    tree1.column("#0", width=0, stretch=NO)
    tree1.heading("#0", text="", anchor=W)
    for col in columns:
        tree1.column(col, anchor=CENTER, width=75, minwidth=140, stretch=YES)
        tree1.heading(col, text=col, anchor=CENTER)

    tree1.pack(padx=5, pady=5, side=LEFT)

    sb1 = ttk.Scrollbar(f1, cursor="circle")
    sb1.pack(pady=5, side=RIGHT, fill=Y)

    f2 = ttk.Frame(mid_frame)
    f2.pack(fill=X, expand=1, anchor=CENTER)
    sb2 = ttk.Scrollbar(f2, orient=HORIZONTAL, cursor="circle")
    sb2.pack(pady=5, fill=X, expand=1)

    tree1.configure(yscrollcommand=sb1.set, xscrollcommand=sb2.set)
    sb1.configure(command=tree1.yview)
    sb2.configure(command=tree1.xview)

    tree1.bind("<ButtonRelease-1>", lambda event: get_selected_row(tree1, e1))

    # bottom frame
    bottom_frame = ttk.Frame(frame)
    bottom_frame.pack(fill=X, expand=1)
    frame1 = ttk.Frame(bottom_frame)
    frame1.pack(anchor=CENTER)

    if type(obj) == Machine:
        b1 = ttk.Button(frame1, text="Add", command=lambda: add_machine(nb, tree1))
        b3 = ttk.Button(frame1, text="Update", command=lambda: add_machine(nb, tree1, True))
    else:
        b1 = ttk.Button(frame1, text="Add", command=lambda: sign_up(nb, tree1))
        b3 = ttk.Button(frame1, text="Update", command=lambda: sign_up(nb, tree1, True))

    b2 = ttk.Button(frame1, text="Delete", command=lambda: delete_data(nb, tree1, e1))
    b4 = ttk.Button(frame1, text="View All", command=lambda: view_all_data(nb, tree1, e1))
    b5 = ttk.Button(frame1, text="Clear", command=lambda: clear_screen(nb, tree1, e1))
    b6 = ttk.Button(frame1, text="Delete All Data", command=lambda: delete_all_data(nb, tree1, e1))

    b1.grid(row=0, column=0, padx=10, pady=5)
    b2.grid(row=0, column=1, padx=10, pady=5)
    b3.grid(row=0, column=2, padx=10, pady=5)
    b4.grid(row=0, column=3, padx=10, pady=5)
    b5.grid(row=0, column=4, padx=10, pady=5)
    b6.grid(row=0, column=5, padx=10, pady=5)

    return frame


def get_selected_row(tree, entry):

    try:
        selection = tree.selection()[0]
        email = tree.item(selection, 'values')[0]
        entry.delete(0, END)
        entry.insert(0, email)
    except IndexError:
        pass


def update_usage_time(widget):
    sec = 0
    while not logged_out:
        mins, sec = divmod(sec, 60)
        hr, mins = divmod(mins, 60)
        usage_time = "{:02}:{:02}:{:02} hours".format(hr, mins, sec)
        widget['text'] = usage_time
        widget['font'] = "arial 14"
        time.sleep(1)
        sec += 1


def generate_fees(h, m):
    h = int(h)
    m = int(m)

    if h <= 1:
        if m <= 15:
            return 20
        elif m <= 30:
            return 50
        elif m <= 45:
            return 70
        else:
            return 100
    elif h <= 2:
        if m <= 30:
            return 160
        else:
            return 200
    else:
        return h*100


def calc_time():
    start_time = time.strftime("%X")
    day = time.strftime("%A")
    date = time.strftime("%x").split('/')[0]
    month = time.strftime("%B")
    year = time.strftime("%Y")
    full = (start_time, day, f"{month} {date}, {year}")

    return full


# NOTE: Database Functions
def view_profile(email):
    temp_frame.pack_forget()
    global profile_frame
    profile_frame = ttk.Frame(root)
    profile_frame.pack(fill=BOTH, expand=1)

    welcome_lbl = ttk.Label(profile_frame, text="PROFILE", font="Helvetica 28 bold italic")
    welcome_lbl.pack(padx=10, pady=10)

    data_frame = ttk.Frame(profile_frame)
    data_frame.pack(padx=10, pady=10)

    data = user.search_data(email)[0]

    email_id_lbl = ttk.Label(data_frame, text="Email-Id ", font="Arial 12")
    name_lbl = ttk.Label(data_frame, text="Name :", font="Arial 12")
    contact_no_lbl = ttk.Label(data_frame, text="Contact_no :", font="Arial 12")
    password_lbl = ttk.Label(data_frame, text="Password :", font="Arial 12")
    reg_date_lbl = ttk.Label(data_frame, text="Registration Date :", font="Arial 12")
    reg_day_lbl = ttk.Label(data_frame, text="Registration Day :", font="Arial 12")
    membership_lbl = ttk.Label(data_frame, text="Membership :", font="Arial 12")
    security_lbl = ttk.Label(data_frame, text="Security :", font="Arial 12")
    balance_lbl = ttk.Label(data_frame, text="Balance :", font="Arial 12")

    email_id_show = ttk.Label(data_frame, text=data[0], font="Arial 12")
    name_show = ttk.Label(data_frame, text=data[1], font="Arial 12")
    contact_no_show = ttk.Label(data_frame, text="+91 " + data[2], font="Arial 12")
    password_show = ttk.Label(data_frame, text=data[3], font="Arial 12")
    reg_date_show = ttk.Label(data_frame, text=data[4], font="Arial 12")
    reg_day_show = ttk.Label(data_frame, text=data[5], font="Arial 12")
    membership_show = ttk.Label(data_frame, text=data[6], font="Arial 12")
    security_show = ttk.Label(data_frame, text="Rs. " + data[7], font="Arial 12")
    balance_show = ttk.Label(data_frame, text="Rs. " + data[8], font="Arial 12")

    email_id_lbl.grid(row=0, column=0, padx=10, pady=5, sticky=E)
    name_lbl.grid(row=1, column=0, padx=10, pady=5, sticky=E)
    contact_no_lbl.grid(row=2, column=0, padx=10, pady=5, sticky=E)
    password_lbl.grid(row=3, column=0, padx=10, pady=5, sticky=E)
    reg_date_lbl.grid(row=4, column=0, padx=10, pady=5, sticky=E)
    reg_day_lbl.grid(row=5, column=0, padx=10, pady=5, sticky=E)
    membership_lbl.grid(row=6, column=0, padx=10, pady=5, sticky=E)
    security_lbl.grid(row=7, column=0, padx=10, pady=5, sticky=E)
    balance_lbl.grid(row=8, column=0, padx=10, pady=5, sticky=E)

    email_id_show.grid(row=0, column=1, padx=10, pady=5, sticky=W)
    name_show.grid(row=1, column=1, padx=10, pady=5, sticky=W)
    contact_no_show.grid(row=2, column=1, padx=10, pady=5, sticky=W)
    password_show.grid(row=3, column=1, padx=10, pady=5, sticky=W)
    reg_date_show.grid(row=4, column=1, padx=10, pady=5, sticky=W)
    reg_day_show.grid(row=5, column=1, padx=10, pady=5, sticky=W)
    membership_show.grid(row=6, column=1, padx=10, pady=5, sticky=W)
    security_show.grid(row=7, column=1, padx=10, pady=5, sticky=W)
    balance_show.grid(row=8, column=1, padx=10, pady=5, sticky=W)

    bottom_frame = ttk.Frame(profile_frame)
    bottom_frame.pack(padx=10)

    back_btn1 = ttk.Button(bottom_frame, text="Back", command=lambda: back(temp_frame, profile_frame))
    back_btn1.pack(padx=10, pady=10)


def register(nb, obj, vals, email_txt=None, update=False):
    try:
        # check empty fields
        for key in vals.keys():
            val = vals[key].get()
            if val == "":
                raise EmptyFieldError("Empty Fields!!", key)

        # check email-id
        if not update:
            email = vals["Email"].get()
            email_regex = re.compile(r'^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
            match = email_regex.search(email) is None
            if match:
                raise InvalidFormatError("Invalid Email Format!!", "Email")

        # check contact number
        no = vals["Contact Number"].get()
        try:
            int(no)
        except ValueError:
            messagebox.showerror(title="Invalid Contact Number!!",
                                 message="Contact Number must contain only digits from 0-9!")
            return

        if len(no) > 10:
            raise InvalidLengthError("Contact Number Too Long!!")
        elif len(no) < 10:
            raise InvalidLengthError("Contact Number Too Short!!")

        # check date
        if not update:
            date = vals["Join Date"].get()
            date_format = '%d/%m/%Y'

            if date == "dd/mm/yyyy":
                raise EmptyFieldError("Empty Fields!!", "Join Date")

            try:
                datetime.datetime.strptime(date, date_format)
            except ValueError:
                messagebox.showerror(title="Invalid Date!!",
                                     message="Please enter a valid date in dd/mm/yyyy format!!")
                return

    except EmptyFieldError as e:
        messagebox.showerror(title=e.message, message=f"{e.key} cannot be Empty!!")
        return
    except InvalidFormatError as e:
        messagebox.showerror(title=e.message, message=f"{e.key} has invalid format!!")
        return
    except InvalidLengthError as e:
        messagebox.showerror(title=e.message, message="Contact number must contain exactly 10 digits!!")
        return

    if not update:
        email = vals["Email"].get()
        check = obj.check_data(email)

        if len(check) == 0:
            obj.insert_data(vals)
            messagebox.showinfo(title="Registration Successful!!", message="You have been successfully registered!")

            for key in vals.keys():
                vals[key].delete(0, END)

            if type(obj) == User:
                vals["Membership"].set("12 month")
        else:
            messagebox.showerror(title="Registration Failed!!",
                                 message="The given Email-Id already exists!!")
    else:
        obj.update_data(email_txt, vals)
        messagebox.showinfo(title="Update Successful!!", message="Record has been successfully updated!")


def register_machine(nb, vals, model=None, update=False):
    try:
        # check empty fields
        for key in vals.keys():
            val = vals[key].get()
            if val == "":
                raise EmptyFieldError("Empty Fields!!", key)

        # check price
        p = vals["Price"].get()
        try:
            float(p)
        except ValueError:
            messagebox.showerror(title="Invalid Price!!",
                                 message="Price must contain only digits from 0-9 or a decimal point!")
            return

        # check date
        date = vals["Buy Date"].get()
        date_format = '%d/%m/%Y'

        if date == "dd/mm/yyyy":
            raise EmptyFieldError("Empty Fields!!", "Join Date")
        try:
            datetime.datetime.strptime(date, date_format)
        except ValueError:
            messagebox.showerror(title="Invalid Date!!",
                                 message="Please enter a valid date in dd/mm/yyyy format!!")
            return

    except EmptyFieldError as e:
        messagebox.showerror(title=e.message, message=f"{e.key} cannot be Empty!!")
        return

    if not update:
        model = vals["Model"].get()
        check = machine.check_data(model)

        if len(check) == 0:
            machine.insert_data(vals)
            messagebox.showinfo(title="Registration Successful!!", message="You have been successfully registered!")

            for key in vals.keys():
                vals[key].delete(0, END)
            vals["Warranty"].set("24 months")
        else:
            messagebox.showerror(title="Registration Failed!!",
                                 message="The given Model No. already exists!!")
    else:
        machine.update_data(model, vals)
        messagebox.showinfo(title="Update Successful!!", message="Record has been successfully updated!")


def search(nb, tree, entry):
    obj = get_object(nb)
    primary_key = entry.get()

    record = obj.search_data(primary_key)

    clear_screen(nb, tree, entry)

    if len(record) != 0:
        tree.insert(parent='', index='end', iid=0, text="", values=record[0], tags=('evenrow',))
    elif entry.get() != "":
        messagebox.showwarning(title="No Record Found",
                               message=f"There is no such record corresponding to email '{entry.get()}' !!")
        return


def delete_data(nb, tree, entry):
    selections = tree.selection()

    if len(selections) == 0:
        messagebox.showerror(title="Select some record(s)", message="Please select at least one record to delete!")
        return

    response = messagebox.askokcancel(title="Confirm Deletion",
                                      message="You are about to permanently delete the selection(s)! This action cannot"
                                              " be reversed!!\nPress OK to confirm, else press Cancel.")

    if response:
        obj = get_object(nb)

        entry.delete(0, END)

        for idx in selections:
            record = tree.item(idx, 'values')
            obj.delete_data(record[0])
            tree.delete(idx)

    return


def delete_all_data(nb, tree, entry):
    obj = get_object(nb)

    src_db = type(obj).__name__
    response = messagebox.askokcancel(title="Confirm Deletion",
                                      message=f"You are about to permanently delete the whole '{src_db}' Database! This"
                                              f" action cannot be reversed!!\nPress OK to confirm, else press Cancel.")

    if response:
        obj.delete_all_data()
        clear_screen(nb, tree, entry)

    return


def view_all_data(nb, tree, entry):
    obj = get_object(nb)

    clear_screen(nb, tree, entry)

    records = obj.view_data()
    for i, row in enumerate(records):
        if i%2 == 0:
            tree.insert(parent='', index='end', iid=i, text="", values=row, tags=('evenrow', ))
        else:
            tree.insert(parent='', index='end', iid=i, text="", values=row, tags=('oddrow', ))


def clear_screen(nb, tree, entry):
    obj = get_object(nb)
    entry.delete(0, END)

    for record in tree.get_children():
        tree.delete(record)


# NOTE: COMMAND FUNCTIONS
def back(prev_frame, curr_frame, staff_logged_out=False):

    if staff_logged_out:
        confirm = messagebox.askyesno(title="Logout Confirmation!", message="Are you sure you want to logout?")
        if not confirm:
            return

    if curr_frame == home_frame:
        curr_frame.place_forget()
    else:
        curr_frame.pack_forget()

    if prev_frame == home_frame:
        prev_frame.place(x=0, y=0)
    else:
        prev_frame.pack(fill=BOTH, expand=1)


def add_machine(nb, tree, update=False):

    if update:
        selections = tree.selection()

        if len(selections) != 1:
            messagebox.showerror(title="Select a record", message="Please select ONE record to Update!")
            return

    nb.pack_forget()
    global add_machine_frame
    add_machine_frame = ttk.Frame(root)
    add_machine_frame.pack(fill=BOTH, expand=1)

    if update:
        welcome_lbl = ttk.Label(add_machine_frame, text="Update Record!", font="Helvetica 28 bold italic")
    else:
        welcome_lbl = ttk.Label(add_machine_frame, text="Register!", font="Helvetica 28 bold italic")

    welcome_lbl.pack(padx=10, pady=10)

    reg_frame = ttk.Frame(add_machine_frame)
    reg_frame.pack(padx=10, pady=20)

    model_no_lbl = ttk.Label(reg_frame, text="Model No. :")
    item_lbl = ttk.Label(reg_frame, text="Item :")
    brand_lbl = ttk.Label(reg_frame, text="Brand :")

    if update:
        price_lbl = ttk.Label(reg_frame, text="Extd. Warranty Price :")
        warranty_lbl = ttk.Label(reg_frame, text="Extd. Warranty Period :")
        buy_date_lbl = ttk.Label(reg_frame, text="Extd. Warranty Buy Date :")
    else:
        price_lbl = ttk.Label(reg_frame, text="Price :")
        warranty_lbl = ttk.Label(reg_frame, text="Warranty Period :")
        buy_date_lbl = ttk.Label(reg_frame, text="Date of Purchase :")

    if update:
        selected = tree.selection()[0]
        model, item, brand, _, _, date, day = tree.item(selected, 'values')
        model_no_entry = ttk.Label(reg_frame, text=model)
        item_entry = ttk.Label(reg_frame, text=item)
        brand_entry = ttk.Label(reg_frame, text=brand)
    else:
        model_no_entry = ttk.Entry(reg_frame, width=25)
        item_entry = ttk.Entry(reg_frame, width=25)
        brand_entry = ttk.Entry(reg_frame, width=25)

    price_entry = ttk.Entry(reg_frame, width=25)

    warranty_options = [f"{i} months" for i in range(0, 25) if(i%3)==0]
    warranty_entry = ttk.Combobox(reg_frame, width=25, values=warranty_options)
    warranty_entry.set(warranty_options[-1])
    buy_date_entry = EntryWithPlaceholder(reg_frame, "dd/mm/yyyy", width=25)

    model_no_lbl.grid(row=0, column=0, padx=14, pady=5, sticky=E)
    item_lbl.grid(row=1, column=0, padx=14, pady=5, sticky=E)
    brand_lbl.grid(row=2, column=0, padx=14, pady=5, sticky=E)
    price_lbl.grid(row=3, column=0, padx=14, pady=5, sticky=E)
    warranty_lbl.grid(row=4, column=0, padx=14, pady=5, sticky=E)
    buy_date_lbl.grid(row=5, column=0, padx=14, pady=5, sticky=E)

    model_no_entry.grid(row=0, column=1, padx=1, pady=5, sticky=W)
    item_entry.grid(row=1, column=1, padx=1, pady=5, sticky=W)
    brand_entry.grid(row=2, column=1, padx=1, pady=5, sticky=W)
    price_entry.grid(row=3, column=1, padx=1, pady=5, sticky=W)
    warranty_entry.grid(row=4, column=1, padx=1, pady=5, sticky=W)
    buy_date_entry.grid(row=5, column=1, padx=1, pady=5, sticky=W)

    data_vars = {"Price": price_entry, "Warranty": warranty_entry, "Buy Date": buy_date_entry}

    if not update:
        data_vars["Model"] = model_no_entry
        data_vars["Item"] = item_entry
        data_vars["Brand"] = brand_entry

    bottom_frame = ttk.Frame(add_machine_frame)
    bottom_frame.pack(padx=10)

    if update:
        sign_up_btn = ttk.Button(bottom_frame, text="UPDATE!", command=lambda: register_machine(nb, data_vars, model, True))
    else:
        sign_up_btn = ttk.Button(bottom_frame, text="REGISTER!", command=lambda: register_machine(nb, data_vars))

    sign_up_btn.pack(padx=30, pady=1, side=LEFT)
    back_btn = ttk.Button(bottom_frame, text="Back", command=lambda: back(nb, add_machine_frame))
    back_btn.pack(padx=30, pady=10, side=RIGHT)


def clear_fields(email_entry, password_entry):
    email_entry.delete(0, END)
    password_entry.delete(0, END)


def sign_up(nb, tree, update=False):
    if update:
        selections = tree.selection()

        if len(selections) != 1:
            messagebox.showerror(title="Select a record", message="Please select ONE record to Update!")
            return

    nb.pack_forget()
    global sign_up_frame
    sign_up_frame = ttk.Frame(root)
    sign_up_frame.pack(fill=BOTH, expand=1)

    if update:
        welcome_lbl = ttk.Label(sign_up_frame, text="Update Record!", font="Helvetica 28 bold italic")
    else:
        welcome_lbl = ttk.Label(sign_up_frame, text="Sign-Up!", font="Helvetica 28 bold italic")

    welcome_lbl.pack(padx=10, pady=10)

    reg_frame = ttk.Frame(sign_up_frame)
    reg_frame.pack(padx=10, pady=20)

    name_lbl = ttk.Label(reg_frame, text="Full Name :")
    email_lbl = ttk.Label(reg_frame, text="Email Id :")
    password_lbl = ttk.Label(reg_frame, text="Password :")
    contact_no_lbl = ttk.Label(reg_frame, text="Contact Number :")
    join_date_lbl = ttk.Label(reg_frame, text="Registration Date :")

    if update:
        selection = tree.selection()[0]
        email = tree.item(selection, 'values')[0]
        join_date = tree.item(selection, 'values')[4]
        email_entry = ttk.Label(reg_frame, text=email)
        join_date_entry = ttk.Label(reg_frame, text=join_date)
    else:
        email_entry = ttk.Entry(reg_frame, width=25)
        join_date_entry = EntryWithPlaceholder(reg_frame, "dd/mm/yyyy", width=25)

    name_entry = ttk.Entry(reg_frame, width=25)
    password_entry = ttk.Entry(reg_frame, width=25, show="*")
    contact_no_entry = ttk.Entry(reg_frame, width=25)

    name_lbl.grid(row=0, column=0, padx=14, pady=5, sticky=E)
    email_lbl.grid(row=1, column=0, padx=14, pady=5, sticky=E)
    password_lbl.grid(row=2, column=0, padx=14, pady=5, sticky=E)
    contact_no_lbl.grid(row=3, column=0, padx=14, pady=5, sticky=E)
    join_date_lbl.grid(row=4, column=0, padx=14, pady=5, sticky=E)

    name_entry.grid(row=0, column=1, padx=1, pady=5, sticky=W)
    email_entry.grid(row=1, column=1, padx=1, pady=5, sticky=W)
    password_entry.grid(row=2, column=1, padx=1, pady=5, sticky=W)
    contact_no_entry.grid(row=3, column=1, padx=1, pady=5, sticky=W)
    join_date_entry.grid(row=4, column=1, padx=1, pady=5, sticky=W)

    data_vars = {"Name": name_entry, "Password": password_entry, "Contact Number": contact_no_entry}

    if not update:
        data_vars["Email"] = email_entry
        data_vars["Join Date"] = join_date_entry

    obj = get_object(nb)

    if type(obj) == User:
        membership_lbl = ttk.Label(reg_frame, text="Membership Period :")
        membership_options = [f"12 months (Rs. {sec_deposit['12 months']})",
                              f"6 months (Rs. {sec_deposit['6 months']})",
                              f"3 months (Rs. {sec_deposit['3 months']})",
                              f"1 month (Rs. {sec_deposit['1 month']})",
                              f"0 months (Rs. {sec_deposit['0 months']})"]
        if update:
            membership = tree.selection()[0]
            membership = tree.item(membership, 'values')[6]
            membership_option = ttk.Label(reg_frame, text=membership)
        else:
            membership_option = ttk.Combobox(reg_frame, width=25, values=membership_options)
            membership_option.set(membership_options[0])
            data_vars["Membership"] = membership_option

        membership_lbl.grid(row=5, column=0, padx=14, pady=5, sticky=E)
        membership_option.grid(row=5, column=1, padx=1, pady=5, sticky=W)

    if type(obj) == Staff:
        salary_lbl = ttk.Label(reg_frame, text="Salary :")
        salary_var = StringVar()
        salary_entry = ttk.Entry(reg_frame, width=25, textvariable=salary_var)
        salary_lbl.grid(row=5, column=0, padx=14, pady=5, sticky=E)
        salary_entry.grid(row=5, column=1, padx=1, pady=5, sticky=W)
        data_vars["Salary"] = salary_entry

    toggle_btn1 = TogglePasswordButton("show", reg_frame)
    toggle_btn2 = TogglePasswordButton("hide", reg_frame)
    params = {"row": 2, "column": 2, "padx": 1}
    toggle_btn1.grid(params)
    buttons = (toggle_btn1, toggle_btn2)
    toggle_btn1['command'] = lambda: toggle_btn1.toggle_passwd(password_entry, buttons, **params)

    bottom_frame = ttk.Frame(sign_up_frame)
    bottom_frame.pack(padx=10)

    if update:
        sign_up_btn = ttk.Button(bottom_frame, text="UPDATE!", command=lambda: register(nb, obj, data_vars, email, True))
    else:
        sign_up_btn = ttk.Button(bottom_frame, text="REGISTER!", command=lambda: register(nb, obj, data_vars))

    sign_up_btn.pack(padx=30, pady=1, side=LEFT)
    back_btn = ttk.Button(bottom_frame, text="Back", command=lambda: back(nb, sign_up_frame))
    back_btn.pack(padx=30, pady=10, side=RIGHT)


def user_logged_out(curr_frame, widget, email):
    confirm = messagebox.askyesno(title="Logout Confirmation!", message="Are you sure you want to logout?")
    if confirm:
        time.sleep(0.1)
        global logged_out
        logged_out = True
        update_usage_time(widget)

        time_used = widget['text'].split(' ')[0]
        hrs, mins, _ = time_used.split(':')
        fees = generate_fees(hrs, mins)

        balance = user.deduct_fees(email, fees)

        if balance > 0:
            messagebox.showinfo(title="Successfully Logged Out!", message=f"Your Usage Time is: {widget['text']}"
                                                                          f"\nFees incurred is: Rs. {fees}"
                                                                          f"\nCurrent Balance is: Rs. {balance}")
        elif balance < 0:
            messagebox.showwarning(title="Logout Failed!!", message=f"Your usage has exceeded the Security Deposit by Rs. "
                                                                    f"{-balance}.\nPlease clear your due by contacting staff!")
        else:
            messagebox.showwarning(title="Zero Balance Warning!!", message=f"Your remaining balance is Rs. 0 !\nTo use your "
                                                                           f"account further, please renew your membership!")

        back(log_in_frame, curr_frame)


def user_logged_in(curr_frame, vals):
    email = vals[0].get()
    passwd = vals[1].get()

    try:
        if email == "" or passwd == "":
            raise EmptyFieldError("Empty Credentials")

        # check email-id
        email_regex = re.compile(r'^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        match = email_regex.search(email) is None
        if match:
            raise InvalidFormatError("Invalid Email Format!!", "Email")
        if len(user.check_data(email)) == 0:
            raise MatchNotFoundError("Invalid Credentials")

        # check remaining balance
        balance = user.check_balance(email)
        if balance <= 0:
            messagebox.showerror(title="Insufficient Balance!!", message="You have exhausted the allowed usage for your "
                                                                         "Membership!\nTo further use our services, please "
                                                                         "renew your membership")
            return

    except EmptyFieldError as e:
        messagebox.showerror(title=e.message, message="Email-ID or Password cannot be empty!!")
    except InvalidFormatError as e:
        messagebox.showerror(title=e.message, message=f"{e.key} has invalid format!!")
    except MatchNotFoundError as e:
        messagebox.showerror(title=e.message, message="There is no such user with given Email-ID or Password!!"
                                                      "\nPlease try again!")

    else:
        messagebox.showinfo(title="IMPORTANT!!", message="Your usage time is now being recorded!"
                                                         "\nTo stop, press Logout!")
        global logged_out
        logged_out = False
        curr_frame.pack_forget()

        global temp_frame
        temp_frame = ttk.Frame(root)
        temp_frame.pack(fill=BOTH, expand=1)

        msg_lbl = ttk.Label(temp_frame, text="Successfully Logged In!", font="Helvetica 20 bold italic")
        msg_lbl.pack(pady=10)

        time_frame = ttk.Frame(temp_frame)
        time_frame.pack(padx=10, pady=(30,10))

        start_time, day, start_date = calc_time()

        curr_time_label1 = ttk.Label(time_frame, text="Logged in at: ", font="arial 14")
        curr_time_label2 = ttk.Label(time_frame, text=f"{day} - {start_date} - {start_time}", font="arial 14")
        usage_time_label1 = ttk.Label(time_frame, text="Current usage time: ", font="arial 14")
        usage_time_label2 = ttk.Label(time_frame)

        curr_time_label1.grid(row=0, column=0, padx=10, pady=10, sticky=E)
        curr_time_label2.grid(row=0, column=1, padx=10, pady=10, sticky=W)
        usage_time_label1.grid(row=1, column=0, padx=10, pady=10, sticky=E)
        usage_time_label2.grid(row=1, column=1, padx=10, pady=10, sticky=W)

        t1 = threading.Thread(target=update_usage_time, args=(usage_time_label2, ), daemon=True)
        t1.start()

        bottom_frame = ttk.Frame(temp_frame)
        bottom_frame.pack(padx=10, pady=20)
        profile_btn = ttk.Button(bottom_frame, text="View Profile", command=lambda: view_profile(email))
        logout_btn = ttk.Button(bottom_frame, text="Logout",
                                command=lambda: user_logged_out(temp_frame, usage_time_label2, email))
        profile_btn.pack(padx=20, side=LEFT)
        logout_btn.pack(padx=20, side=RIGHT)


def user_log_in(curr_frame):
    curr_frame.pack_forget()
    global log_in_frame
    log_in_frame = ttk.Frame(root)
    log_in_frame.pack(fill=BOTH, expand=1)

    # top frame
    top_frame = ttk.Frame(log_in_frame)
    top_frame.pack(padx=10, pady=10)

    welcome_lbl = ttk.Label(top_frame, text="Log-In!", font="Helvetica 28 bold italic")
    msg = "NOTE: As soon as you log-in to your valid account, your usage time will be recorded until you " \
          "logout successfully. Fees will be incurred according to your usage time as per specified rates."
    info_lbl = ttk.Label(top_frame, text=msg, font="Helvetica 11 italic", wraplength=app_width-40)

    welcome_lbl.pack(padx=10, pady=10)
    info_lbl.pack(pady=10)

    # middle frame
    middle_frame = ttk.Frame(log_in_frame)
    middle_frame.pack(padx=10, pady=20)

    email_lbl = ttk.Label(middle_frame, text="Email-ID :")
    password_lbl = ttk.Label(middle_frame, text="Password :")

    email_var = StringVar()
    password_var = StringVar()

    email_entry = ttk.Entry(middle_frame, textvariable=email_var, width=30)
    password_entry = ttk.Entry(middle_frame, textvariable=password_var, width=30, show='*')

    email_lbl.grid(row=0, column=0, padx=10, pady=10, sticky=W)
    password_lbl.grid(row=1, column=0, padx=10, pady=10, sticky=W)

    email_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    toggle_btn1 = TogglePasswordButton("show", middle_frame)
    toggle_btn2 = TogglePasswordButton("hide", middle_frame)
    params = {"row": 1, "column": 2, "padx": 2}
    toggle_btn1.grid(params)
    buttons = (toggle_btn1, toggle_btn2)
    toggle_btn1['command'] = lambda: toggle_btn1.toggle_passwd(password_entry, buttons, **params)

    var_list = (email_var, password_var)
    bottom_frame = ttk.Frame(log_in_frame)
    bottom_frame.pack(padx=10, pady=5)

    login_btn = ttk.Button(bottom_frame, text="LOG IN!", command=lambda: user_logged_in(log_in_frame, var_list))
    login_btn.grid(row=0, column=0, padx=15, pady=5)

    email_entry.bind('<Return>', lambda event, f=log_in_frame, vl=var_list: user_logged_in(f, vl))
    password_entry.bind('<Return>', lambda event, f=log_in_frame, vl=var_list: user_logged_in(f, vl))

    clrscr_btn = ttk.Button(bottom_frame, text="Clear Fields", command=lambda: clear_fields(email_entry, password_entry))
    clrscr_btn.grid(row=0, column=1, padx=15, pady=5)

    back_btn = ttk.Button(bottom_frame, text="Back", command=lambda: back(curr_frame, log_in_frame))
    back_btn.grid(row=0, column=2, padx=15, pady=5)


def staff_logged_in(curr_frame, vals):
    email = vals[0].get()
    passwd = vals[1].get()

    try:
        if email == "" or passwd == "":
            raise EmptyFieldError("Empty Credentials")

        # check email-id
        email_regex = re.compile(r'^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        match = email_regex.search(email) is None
        if match:
            raise InvalidFormatError("Invalid Email Format!!", "Email")
        if len(staff.check_data(email)) == 0:
            raise MatchNotFoundError("Invalid Credentials")

    except EmptyFieldError as e:
        messagebox.showerror(title=e.message, message="Email-ID or Password cannot be empty!!")
    except InvalidFormatError as e:
        messagebox.showerror(title=e.message, message=f"{e.key} has invalid format!!")
    except MatchNotFoundError as e:
        messagebox.showerror(title=e.message, message="There is no such staff member with given Email-ID or Password!!"
                                                      "\nPlease try again!")
    else:
        curr_frame.pack_forget()
        notebook = ttk.Notebook(root)
        notebook.pack(fill=BOTH, expand=1)

        user_mngr_frame = create_tab(notebook, "User Data Manager", "Email-ID", curr_frame)
        staff_mngr_frame = create_tab(notebook, "Staff Data Manager", "Email-ID", curr_frame)
        machine_mngr_frame = create_tab(notebook, "Machine Data Manager", "Model No.", curr_frame)

        notebook.add(user_mngr_frame, text="User Manager")
        notebook.add(staff_mngr_frame, text="Staff Manager")
        notebook.add(machine_mngr_frame, text="Machine Manager")


def staff_log_in(curr_frame):
    curr_frame.pack_forget()
    global staff_login_frame
    staff_login_frame = ttk.Frame(root)
    staff_login_frame.pack(fill=BOTH, expand=1)

    title_lbl = ttk.Label(staff_login_frame, text="Sign-In!", font="Helvetica 30 bold italic")
    title_lbl.pack(padx=20, pady=20)

    temp_frame = ttk.Frame(staff_login_frame)
    temp_frame.pack(padx=20, pady=(30,20))

    email_lbl = ttk.Label(temp_frame, text="Email-ID :")
    password_lbl = ttk.Label(temp_frame, text="Password :")

    email_var = StringVar()
    password_var = StringVar()

    email_entry = ttk.Entry(temp_frame, textvariable=email_var, width=30)
    password_entry = ttk.Entry(temp_frame, textvariable=password_var, width=30, show="*")

    email_lbl.grid(row=0, column=0, padx=10, pady=10, sticky=W)
    password_lbl.grid(row=1, column=0, padx=10, pady=10, sticky=W)

    email_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    toggle_btn1 = TogglePasswordButton("show", temp_frame)
    toggle_btn2 = TogglePasswordButton("hide", temp_frame)
    params = {"row": 1, "column": 2, "padx": 2}
    toggle_btn1.grid(params)
    buttons = (toggle_btn1, toggle_btn2)
    toggle_btn1['command'] = lambda: toggle_btn1.toggle_passwd(password_entry, buttons, **params)

    var_list = (email_var, password_var)

    bottom_frame = ttk.Frame(staff_login_frame)
    bottom_frame.pack(padx=10, pady=10)
    login_btn = ttk.Button(bottom_frame, text="LOG IN!", command=lambda: staff_logged_in(staff_login_frame, var_list))
    login_btn.grid(row=0, column=0, padx=15, pady=5)

    email_entry.bind('<Return>', lambda event, f=staff_login_frame, vl=var_list: staff_logged_in(f, vl))
    password_entry.bind('<Return>', lambda event, f=staff_login_frame, vl=var_list: staff_logged_in(f, vl))

    clrscr_btn = ttk.Button(bottom_frame, text="Clear Fields", command=lambda: clear_fields(email_entry, password_entry))
    clrscr_btn.grid(row=0, column=1, padx=15, pady=5)

    back_btn = ttk.Button(bottom_frame, text="Back", command=lambda: back(curr_frame, staff_login_frame))
    back_btn.grid(row=0, column=2, padx=15, pady=5)


if __name__ == '__main__':
    # getting started
    logged_out = True
    user = User()
    staff = Staff()
    machine = Machine()

    # gui window properties
    root = tk.ThemedTk()
    root.get_themes()
    root.set_theme("itft1")
    root.title("CYBER CAFE MANAGEMENT SYSTEM")
    root.iconbitmap("images/icon.ico")
    app_width = 720
    app_height = 440
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - app_width)//2
    y = (screen_height - app_height)//2
    root.geometry(f"{app_width}x{app_height}+{x}+{y-40}")

    # gui window content
    bg_img = Image.open(r"images\cybercafe_img.png")
    img2 = Image.open(r"images\white_bg.png").convert("RGBA")
    bg_img = Image.blend(bg_img, img2, 0.35).convert("RGBA")
    draw = ImageDraw.Draw(bg_img)
    font1 = ImageFont.truetype(r"fonts\Bungee-Inline.otf", 54)
    points = 120, 10
    label = "WELCOME TO\n1NET CYBER CAFE!"
    color = "#2bff00"
    draw.text(points, label, color, font=font1, align="center")
    bg_img = ImageTk.PhotoImage(bg_img)

    home_frame = Canvas(root, relief=FLAT, background="black", width=app_width, height=app_height)
    home_frame.place(x=0, y=0)
    home_frame.create_image(0, 0, image=bg_img, anchor=NW)

    user_login_btn = ttk.Button(root, text="USER LOGIN", command=lambda: user_log_in(home_frame))
    staff_login_btn = ttk.Button(root, text="STAFF LOGIN", command=lambda: staff_log_in(home_frame))

    user_login_btn.place(x=240, y=200)
    staff_login_btn.place(x=400, y=200)

    root.mainloop()
