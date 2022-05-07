import threading
import tkinter as tk
import tkinter.font as font
from tkinter import *
from tkinter import filedialog as fd
import pickle
from PIL import ImageFile, Image, ImageTk
from PIL import ImageFile, Image, ImageTk
import os
import socket
import re
from MyClasses import user, client, network, bool_and_string, file, username_filename_and_group, group_object, client_join_request
import io
import time
import docx

ImageFile.LOAD_TRUNCATED_IMAGES = True

#main

def threaded_func(func, args):
    if not args:
        t = threading.Thread(target=func)
        t.start()

    else:
        t = threading.Thread(target=func, args=args)
        t.start()

def on_closing():
    disconnect_user2()
    This_Client.user = None
    This_Client.net.net_socket.close()
    root.destroy()

def group_send_file():
    global current_group_shown
    call_net_send_file(This_Client.net, get_path(), False, "", current_group_shown)

def choose_file_to_send(is_group):
    global filename_textbox
    global groups_filename_textbox

    try:
        filename_textbox.config(state=NORMAL)
        filename_textbox.delete(0, END)
    except:
        groups_filename_textbox.config(state=NORMAL)
        groups_filename_textbox.delete(0, END)


    if(is_group != "selected"):
        try:
            filename_textbox.insert(0, "please choose group")
            filename_textbox.config(state=DISABLED)
        except:
            groups_filename_textbox.insert(0, "please choose group")
            groups_filename_textbox.config(state=DISABLED)
        return

    try:
        filename_textbox.config(state="normal")
        filename_textbox.delete(0, "end")
    except:
        groups_filename_textbox.config(state="normal")
        groups_filename_textbox.delete(0, "end")

    global filename
    filename = fd.askopenfilename(title='choose a file', initialdir='/')
    print(filename)
    if(str(filename) == ""):
        try:
            filename_textbox.insert(0, "please choose path")
            filename_textbox.config(state=DISABLED)
        except:
            groups_filename_textbox.insert(0, "please choose path")
            groups_filename_textbox.config(state=DISABLED)
    else:
        try:
            filename_textbox.insert(0, str(filename).split("/")[len(str(filename).split("/"))-1])
            filename_textbox.config(state=DISABLED)
        except:
            groups_filename_textbox.insert(0, str(filename).split("/")[len(str(filename).split("/")) - 1])
            groups_filename_textbox.config(state=DISABLED)

    try:
        filename_textbox.config(state=DISABLED)
    except:
        groups_filename_textbox.config(state=DISABLED)

def choose_where_to_save():
    global directory_textbox
    global groups_textbox
    try:
        directory_textbox.config(state="normal")
        directory_textbox.delete(0, "end")
    except:
        groups_textbox.config(state="normal")
        groups_textbox.delete(0, "end")
    global directory
    directory = fd.askdirectory(title='choose a directory', initialdir='/')
    if(str(directory) == r"C:\Users\User\PycharmProjects\FinalProject"):
        try:
            directory_textbox.insert(0, "please choose directory")
            directory_textbox.config(state=DISABLED)
        except:
            groups_textbox.insert(0, "please choose directory")
            groups_textbox.config(state=DISABLED)
    return directory

def get_path():
    global path
    return path.get()

def fix_group_files_listbox_var(files_listbox_var):
    arr = files_listbox_var.split(",")
    arr.pop()
    str = ",".join(arr)
    return str

def create_specific_listbox():
    global listbox
    listbox.destroy()

    global search_var
    search_par = search_var.get()

    arr = get_user_filenames(This_Client.user.username)
    arr2 = []
    for filename in arr:
        x = re.findall(search_par, filename)
        if(x != []):
            arr2.append(filename)

    create_listbox("destroy", arr2)

def create_users_group_listbox(arr_of_groups):
    global frame_groups

    global users_groups_listbox
    users_groups_listbox = Listbox(frame_groups, height=4,
                      width=16,
                      bg=listbox_color,
                      activestyle='dotbox',
                      font=("calibri", 20),
                      fg="white",
                      exportselection=False)


    index = 1
    while (index < len(arr_of_groups) + 1):
        users_groups_listbox.insert(index, arr_of_groups[index - 1])
        index = index + 1

    global groups_listbox_var
    groups_listbox_var = ""

    return users_groups_listbox

def create_users_listbox():
    global frame_groups

    global users_listbox
    users_listbox = Listbox(frame_groups, height=4,
                                    width=16,
                                    bg=listbox_color,
                                    activestyle='dotbox',
                                    font=("calibri", 20),
                                    fg="white",
                                    exportselection=False)

    global users_listbox_var
    users_listbox_var = ""

    return users_listbox

def call_net_disconnect_chan(member, group):
    net.send_flag("kick member")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send((member + "," + group).encode())


def kick_user():
    global current_group_shown
    global users_listbox_var
    if(users_listbox_var != "" and current_group_shown != "" and This_Client.user.username != users_listbox_var):
        call_net_disconnect_chan(users_listbox_var, current_group_shown)
        db_answer = net.net_socket.recv(30).decode()
        print(db_answer)
        groups_page()


def show_group_data(group_name):
    if(group_name != ""):
        global close_group_button
        global kick_member_button
        global frame_groups
        print(group_name)
        global users_lb
        users_lb.delete(0, END)
        global group_files_listbox
        group_files_listbox.delete(0, END)
        global users_arr
        users_arr = call_net_get_groups_members(group_name)
        insert_members_into_users_listbox(users_arr)
        files_arr = call_net_get_groups_files(group_name)
        insert_files_into_files_listbox(files_arr)
        global is_selected
        is_selected = "selected"
        global current_group_shown
        current_group_shown = group_name
        users_listbox.bind('<<ListboxSelect>>', users_onselect)

        global groups_listbox_var
        groups_listbox_var = ""
        global files_listbox_var
        files_listbox_var = ""
        global users_listbox_var
        users_listbox_var = ""

        try:
            print("button closed")
            close_group_button.destroy()
            kick_member_button.destroy()
        except:
            print("button not closed")
            pass

        close_group_button = tk.Button(frame_groups, text="close", height=1, width=6, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                       command=lambda: threaded_func(close_group, None))
        close_group_button['font'] = myFont

        kick_member_button = tk.Button(frame_groups, text="kick", height=1, width=6, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                       command=lambda: threaded_func(kick_user, None))
        kick_member_button['font'] = myFont

        if(This_Client.user.username == users_arr[0]):
            print("you the host")
            close_group_button.pack()
            close_group_button.place(relx=0.805, rely=0.525)

            kick_member_button.pack()
            kick_member_button.place(relx=0.805, rely=0.625)

def close_group():
    global current_group_shown
    call_net_close_group(current_group_shown)
    groups_page()

def insert_members_into_users_listbox(members_arr):
    print(members_arr)
    global users_lb
    index = 1
    while (index < len(members_arr) + 1):
        users_lb.insert(index, members_arr[index - 1])
        index = index + 1
    users_lb.itemconfig(0, {'bg': 'red'})

def insert_files_into_files_listbox(files_arr):
    index = 1
    global group_files_listbox
    while (index < len(files_arr) + 1):
        lb_str = files_arr[index - 1] + "," + files_arr[index]
        group_files_listbox.insert(index, lb_str)
        index = index + 2


def create_group_file_listbox():
    global frame_groups
    global group_files_listbox
    group_files_listbox = Listbox(frame_groups, height=7,
                      width=30,
                      bg=listbox_color,
                      activestyle='dotbox',
                      font=("calibri", 26),
                      fg="white",
                      exportselection=False)
    group_files_listbox.bind('<<ListboxSelect>>', group_files_onselect)

    global files_listbox_var
    files_listbox_var = ""

    group_files_listbox.pack()
    group_files_listbox.place(relx=0.325, rely=0.2)


def create_listbox(flag, arr_of_filenames):
    global listbox

    global search_textbox
    search_textbox.delete(0, END)

    if(flag == "destroy"):
        listbox.destroy()

    listbox = Listbox(frame_request, height=4,
                      width=16,
                      bg=listbox_color,
                      activestyle='dotbox',
                      font=("calibri", 36),
                      fg="white",
                      exportselection=False)
    listbox.bind('<<ListboxSelect>>', onselect)

    index = 1
    while (index < len(arr_of_filenames) + 1):
        listbox.insert(index, arr_of_filenames[index - 1])
        index = index + 1
    listbox.pack()
    listbox.place(relx=0.35, rely=0.4)

    global listbox_var
    listbox_var = ""

def call_net_close_group(group_name):
    net.send_flag("close group")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(group_name.encode())

def call_net_send_and_delete_file(net, file_object):
    global win
    global current_group_shown
    try:
        file_object.group = current_group_shown
    except:
        pass
    net.send_flag("override file")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        with open(filename, 'rb') as opened_file:
            opened_file.seek(0)
            file_bytes = opened_file.read()
        net.send_file(file_bytes, file_object.size)
        net.send_file_object(file_object)
        net.net_socket.send(This_Client.user.username.encode())
        win.destroy()

def call_net_replace_txt_file(net, file_object):
    print(file_object.file)
    net.send_flag("override file")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        print("baranes3")
        with open(file_object.file + ".txt", 'rb') as opened_file:
            opened_file.seek(0)
            print("baranes4")
            file_bytes = opened_file.read()
        print("baranes5")
        net.send_file(file_bytes, file_object.size)
        print("baranes6")
        net.send_file_object(file_object)
        print("baranes7")
        net.net_socket.send(This_Client.user.username.encode())
        print("baranes8")

def get_user_filenames(username):
    net.send_flag("get user filename arr")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(username.encode())

        arr = pickle.loads(net.net_socket.recv(250))
        return arr

def call_net_send_file(net, path, resend_flag, fixed_filename, group_name):
    if(path != "" and path != "please choose path"):
        global filename
        global db_answer_textbox
        global groups_textbox

        type = str(filename).split(".")[len(str(filename).split(".")) - 1]
        size = os.path.getsize(filename)
        if(resend_flag != True):
            file_name = str(filename).split("/")[len(str(filename).split("/"))-1]
            file_name2 = file_name.split(".")
            file_name2.pop()

            file_name3 = ""
            for i in file_name2:
                file_name3 += str(i) + "."
            file_name3 = file_name3[:-1]
            print(file_name3)
        else:
            file_name3 = fixed_filename
        file_object = file(This_Client.user.username, file_name3, type, size, group_name)
        print(len(pickle.dumps(file_object, 0)))

        net.send_flag("sending file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            with open(filename, 'rb') as opened_file:
                opened_file.seek(0)
                file_bytes = opened_file.read()
            net.send_file(file_bytes, size)
            net.send_file_object(file_object)

            db_answer = net.net_socket.recv(250).decode()
            if(resend_flag != True):
                if(db_answer == "your file uploaded successfuly"):
                    try:
                        db_answer_textbox.config(state=NORMAL)
                        db_answer_textbox.delete(0, END)
                        db_answer_textbox.insert(0, db_answer)
                        db_answer_textbox.config(state=DISABLED)
                    except:
                        groups_textbox.config(state=NORMAL)
                        groups_textbox.delete(0, END)
                        groups_textbox.insert(0, db_answer)
                        groups_textbox.config(state=DISABLED)
                else:
                    create_file_alert_window(db_answer, file_object)
            else:
                global win
                win.destroy()



def listbox_of_filenames(arr):
    listbox = Listbox(frame_default, height=4,
                      width=15,
                      bg=listbox_color,
                      activestyle='dotbox',
                      font=("Courier", 44),
                      fg="white",
                      exportselection=False)
    index = 1
    while(index < len(arr) + 1):
        listbox.insert(index, arr[index - 1])
        index = index + 1

    return listbox

def onselect(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    global listbox_var
    listbox_var = value

def groups_onselect(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    global groups_listbox_var
    groups_listbox_var = value

def users_onselect(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    global users_listbox_var
    users_listbox_var = value
    print(users_listbox_var)

def group_files_onselect(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    global files_listbox_var
    files_listbox_var = value


def delete_file(value):
    global listbox
    if (value == listbox.get(ANCHOR)):
        listbox.delete(ANCHOR)

        global current_group_shown
        delete_object = username_filename_and_group(This_Client.user.username, value, current_group_shown)

        net.send_flag("delete file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            net.net_socket.send(pickle.dumps(delete_object, 0))

def delete_group_file(value):
    file_owner = value.split(",")[-1]
    if (This_Client.user.username == users_arr[0] or file_owner == This_Client.user.username):
        global group_files_listbox
        value2 = fix_group_files_listbox_var(value)

        global current_group_shown
        delete_object = username_filename_and_group(file_owner, value2, current_group_shown)

        net.send_flag("delete file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            net.net_socket.send(pickle.dumps(delete_object, 0))

        if(current_group_shown != "Null"):
            groups_page()

    else:
        try:
            global db_answer_textbox
            db_answer_textbox.config(state=NORMAL)
            db_answer_textbox.delete(0, END)
            db_answer_textbox.insert(0, "you dont have permission to delete the file")
            db_answer_textbox.config(state=DISABLED)
        except:
            global groups_textbox
            groups_textbox.config(state=NORMAL)
            groups_textbox.delete(0, END)
            groups_textbox.insert(0, "you dont have permission to delete the file")
            groups_textbox.config(state=DISABLED)



def call_net_send_register(net, first, last, gender, mikum, username, password, re_password, email):
    net.send_flag("sending register data")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.send_register(first, last, gender, mikum, username, password, re_password, email)

def call_net_send_login(net, username, password):
    net.send_flag("sending login data")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.send_login(username, password)
        return (net.net_socket.recv(250).decode())

def call_net_request_file_and_open(requested_filename, group_name):
    if(requested_filename != ""):
        net.send_flag("request file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            requested_filename_with_type = requested_filename
            mini_arr = requested_filename.split(".")
            mini_arr.pop()
            requested_filename = ".".join(mini_arr)
            if (group_name == "Null"):
                net.send_request_file_data(This_Client.user.username, requested_filename, group_name)
            else:
                global files_listbox_var
                file_owner = files_listbox_var.split(",")[-1]
                net.send_request_file_data(file_owner, requested_filename, group_name)

            mini_flag = str(net.net_socket.recv(250).decode())
            if(mini_flag == "found image"):
                rcv_object = net.net_socket.recv(500)
                requested_file_object = pickle.loads(rcv_object)

                requested_file_bytes = b""
                requested_file_bytes += net.net_socket.recv(int(requested_file_object.size))

                mini_arr2 = requested_filename_with_type.split(".")
                file_type = mini_arr2[len(mini_arr2) - 1]
                print(file_type)

                if(file_type == "txt"):
                    txt_file_write_page(requested_file_bytes, requested_file_object)

                elif(file_type == "docx"):
                    with open(requested_file_object.file + '.docx', 'wb') as f:
                        f.seek(0)
                        f.write(requested_file_bytes)
                    os.system(requested_file_object.file + '.docx')
                    os.remove(requested_file_object.file + '.docx')

                else:
                    file_arr = io.BytesIO(requested_file_bytes)
                    opened_file = Image.open(file_arr)
                    opened_file.show()



            else:
                print("no match")

        else:
            print("no match")

def create_group_win():
    global group_name_var
    group_name_var = tk.StringVar()
    global group_passw_var
    group_passw_var = tk.StringVar()
    global group_textbox_check_var
    group_textbox_check_var = tk.StringVar()

    global create_win
    create_win = tk.Toplevel()
    create_win.configure(bg="white")
    create_win.geometry("500x300+125+75")
    create_win.resizable(False, False)
    create_win.grab_set()
    create_group_frame = tk.Frame(create_win)
    create_group_frame.pack(fill='both', expand=True)
    create_group_frame.bind('<Configure>', "500x400")
    write(create_group_frame, "Create", 0.22)

    group_name_text = tk.Label(create_group_frame,
                                text="group name:",
                                fg=button_bg_color,
                                font="calibri 20 underline",
                                bg="white"
                                )
    group_name_text.pack()
    group_name_text.place(relx=0.0525, rely=0.3)

    group_name_textbox = Entry(create_group_frame, textvariable=group_name_var, width=16)
    group_name_textbox.pack()
    group_name_textbox.place(relx=0.4475, rely=0.31)
    group_name_textbox.configure(font=("calibri", 18))

    group_passw_text = tk.Label(create_group_frame,
                               text="password:",
                               fg=button_bg_color,
                               font="calibri 20 underline",
                                bg="white"
                               )
    group_passw_text.pack()
    group_passw_text.place(relx=0.07, rely=0.45)

    group_passw_textbox = Entry(create_group_frame, textvariable=group_passw_var, show="*", width=16)
    group_passw_textbox.pack()
    group_passw_textbox.place(relx=0.4475, rely=0.46)
    group_passw_textbox.configure(font=("calibri", 18))

    global group_textbox_check
    group_textbox_check = Entry(create_group_frame, textvariable=group_textbox_check_var, width=45)
    group_textbox_check.pack()
    group_textbox_check.place(relx=0.15, rely=0.61)
    group_textbox_check.configure(font=("calibri", 10))
    group_textbox_check.config(state=DISABLED)

    create_group_button = tk.Button(create_group_frame, text="create", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=6, command=lambda:threaded_func(create_group_submit, None))
    create_group_button['font'] = myFont
    create_group_button.pack()
    create_group_button.place(relx=0.325, rely=0.725)

def group_name_check(group_name):
    if (len(group_name) > 24 or len(group_name) < 6):
        return bool_and_string(False, "the group name's len should be between 6 to 24")
    if (re.match(r"^[a-zA-Z0-9_.&()-]+$", group_name) == None):
        return bool_and_string(False, "there are bad letters your group name")
    return bool_and_string(True, "")

def group_password_check(password):
    if (len(password) > 16 or len(password) < 6):
        return bool_and_string(False, "the group password's len should be between 6 to 16")
    if (re.match(r"^[a-zA-Z0-9]+$", password) == None):
        return bool_and_string(False, "there are bad letters your group password")
    return bool_and_string(True, "")

def create_group_submit():
    global group_name_var
    global group_passw_var
    global group_textbox_check

    group_name = group_name_var.get()
    group_passw = group_passw_var.get()

    group_name_obj = group_name_check(group_name)
    group_passw_obj = group_password_check(group_passw)

    group_textbox_check.config(state=NORMAL)
    group_textbox_check.delete(0, "end")

    group_obj = group_object(This_Client.user.username, group_name, group_passw, [])

    if(group_name_obj.GetFlag() == False):
        group_textbox_check.delete(0, "end")
        group_textbox_check.insert(0, group_name_obj.GetText())
        group_textbox_check.config(state=DISABLED)

    elif(group_passw_obj.GetFlag() == False):
        group_textbox_check.delete(0, "end")
        group_textbox_check.insert(0, group_passw_obj.GetText())
        group_textbox_check.config(state=DISABLED)

    elif(call_net_create_group(group_obj) == "the group is already exist"):
        group_textbox_check.delete(0, "end")
        group_textbox_check.insert(0, "the group is already exist")
        group_textbox_check.config(state=DISABLED)

    else:
        group_textbox_check.insert(0, "your group created")
        group_textbox_check.config(state=DISABLED)

        global create_win
        create_win.destroy()
        groups_page()


def call_net_create_group(group_obj):
    net.send_flag("create group")
    answer = net.net_socket.recv(20).decode()
    if (answer == "got flag"):
        net.send_group_object(group_obj)
    db_answer = net.net_socket.recv(100).decode()
    return db_answer

def call_net_join_group(request_obj):
    net.send_flag("join group")
    answer = net.net_socket.recv(20).decode()
    if (answer == "got flag"):
        net.send_request_object(request_obj)
    db_answer = net.net_socket.recv(100).decode()
    print(db_answer)
    return db_answer

def join_group_win():
    global group_name_join_var
    group_name_join_var = StringVar()
    global group_passw_join_var
    group_passw_join_var = StringVar()
    global join_group_textbox_check_var
    join_group_textbox_check_var = StringVar()

    global join_win
    join_win = tk.Toplevel()
    join_win.configure(bg="white")
    join_win.geometry("500x300+125+75")
    join_win.resizable(False, False)
    join_win.grab_set()
    join_group_frame = tk.Frame(join_win)
    join_group_frame.pack(fill='both', expand=True)
    join_group_frame.bind('<Configure>', "500x400")
    write(join_group_frame, "Join", 0.2)

    group_name_text = tk.Label(join_group_frame,
                               text="group name:",
                               fg=button_bg_color,
                               font="calibri 20 underline",
                                bg="white"
                               )
    group_name_text.pack()
    group_name_text.place(relx=0.0525, rely=0.3)

    group_name_textbox = Entry(join_group_frame, textvariable=group_name_join_var, width=16)
    group_name_textbox.pack()
    group_name_textbox.place(relx=0.4475, rely=0.31)
    group_name_textbox.configure(font=("calibri", 18))

    group_passw_text = tk.Label(join_group_frame,
                                text="password:",
                                fg=button_bg_color,
                                font="calibri 20 underline",
                                bg="white"
                                )
    group_passw_text.pack()
    group_passw_text.place(relx=0.07, rely=0.45)

    group_passw_textbox = Entry(join_group_frame, textvariable=group_passw_join_var, show="*", width=16)
    group_passw_textbox.pack()
    group_passw_textbox.place(relx=0.4475, rely=0.46)
    group_passw_textbox.configure(font=("calibri", 18))

    global join_group_textbox_check
    join_group_textbox_check = Entry(join_group_frame, textvariable=join_group_textbox_check_var, width=45)
    join_group_textbox_check.pack()
    join_group_textbox_check.place(relx=0.15, rely=0.61)
    join_group_textbox_check.configure(font=("calibri", 10))
    join_group_textbox_check.config(state=DISABLED)

    create_group_button = tk.Button(join_group_frame, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, text="join", height=1, width=6, command=lambda:threaded_func(join_room_submit, None))
    create_group_button['font'] = myFont
    create_group_button.pack()
    create_group_button.place(relx=0.325, rely=0.725)


def join_room_submit():
    global group_name_join_var
    global group_passw_join_var
    global join_group_textbox_check

    group_name_join = group_name_join_var.get()
    group_passw_join = group_passw_join_var.get()
    print(group_name_join)
    print(group_passw_join)

    group_name_join_obj = group_name_check(group_name_join)
    group_passw_join_obj = group_password_check(group_passw_join)

    join_group_textbox_check.config(state=NORMAL)
    join_group_textbox_check.delete(0, "end")

    request_join_obj = client_join_request(This_Client.user.username, group_name_join, group_passw_join)
    group_name_flag = True
    group_passw_flag = True

    if (group_name_join_obj.GetFlag() == False):
        join_group_textbox_check.delete(0, "end")
        join_group_textbox_check.insert(0, group_name_join_obj.GetText())
        join_group_textbox_check.config(state=DISABLED)
        group_name_flag = False

    elif (group_passw_join_obj.GetFlag() == False):
        join_group_textbox_check.delete(0, "end")
        join_group_textbox_check.insert(0, group_passw_join_obj.GetText())
        join_group_textbox_check.config(state=DISABLED)
        group_passw_flag = False

    elif (group_name_flag == True and group_passw_flag == True):
        answer = call_net_join_group(request_join_obj)
        if(answer != "the user joined the group"):
            join_group_textbox_check.delete(0, "end")
            join_group_textbox_check.insert(0, answer)
            join_group_textbox_check.config(state=DISABLED)


        else:
            join_group_textbox_check.insert(0, "the user joined the group")
            join_group_textbox_check.config(state=DISABLED)

            global join_win
            join_win.destroy()
            groups_page()

def call_net_get_users_groups():
    username = This_Client.user.username
    net.send_flag("get users groups")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(username.encode())

        groups_arr = pickle.loads(net.net_socket.recv(1000))
        return groups_arr

def call_net_get_groups_files(group_name):
    net.send_flag("get groups files")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(group_name.encode())

        files_arr = pickle.loads(net.net_socket.recv(4069))
        return files_arr



def call_net_get_groups_members(group_name):
    net.send_flag("get group members")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(group_name.encode())

        users_arr = pickle.loads(net.net_socket.recv(1000))
        return users_arr

def call_net_request_file_and_save(requested_filename, group_name):
    global directory_textbox
    global groups_textbox
    if(requested_filename != ""):
        requested_filename_with_type =requested_filename
        net.send_flag("request file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            mini_arr = requested_filename.split(".")
            mini_arr.pop()
            requested_filename = ".".join(mini_arr)
            if(group_name == "Null"):
                net.send_request_file_data(This_Client.user.username, requested_filename, group_name)
            else:
                global files_listbox_var
                file_owner = files_listbox_var.split(",")[-1]
                net.send_request_file_data(file_owner, requested_filename, group_name)


            mini_flag = str(net.net_socket.recv(100).decode())
            if(mini_flag == "found image"):
                rcv_object = net.net_socket.recv(500)
                requested_file_object = pickle.loads(rcv_object)

                requested_file_bytes = b""
                requested_file_bytes += net.net_socket.recv(int(requested_file_object.size))

                directory_path = os.path.abspath(choose_where_to_save())
                print(directory_path)
                if(directory_path == r"C:\Users\User\PycharmProjects\FinalProject"):
                    try:
                        directory_textbox.config(state=NORMAL)
                        directory_textbox.delete(0, END)
                        directory_textbox.insert(0, "please choose where to save")
                        directory_textbox.config(state=DISABLED)
                    except:
                        groups_textbox.config(state=NORMAL)
                        groups_textbox.delete(0, END)
                        groups_textbox.insert(0, "please choose where to save")
                        groups_textbox.config(state=DISABLED)
                    return
                file_path = os.path.abspath(directory_path + "/" + requested_filename_with_type)
                print(file_path)
                with open(file_path, 'wb') as file:
                    file.seek(0)
                    file.write(requested_file_bytes)
                try:
                    directory_textbox.config(state=NORMAL)
                    directory_textbox.delete(0, END)
                    directory_textbox.insert(0, "your file saved succssesfully")
                    directory_textbox.config(state=DISABLED)
                except:
                    groups_textbox.config(state=NORMAL)
                    groups_textbox.delete(0, END)
                    groups_textbox.insert(0, "your file saved succssesfully")
                    groups_textbox.config(state=DISABLED)



            else:
                try:
                    directory_textbox.config(state=NORMAL)
                    directory_textbox.delete(0, END)
                    directory_textbox.insert(0, "please choose file to save")
                    directory_textbox.config(state=DISABLED)
                except:
                    groups_textbox.config(state=NORMAL)
                    groups_textbox.delete(0, END)
                    groups_textbox.insert(0, "please choose file to save")
                    groups_textbox.config(state=DISABLED)

        else:
            try:
                directory_textbox.config(state=NORMAL)
                directory_textbox.delete(0, END)
                directory_textbox.insert(0, "please choose file to save")
                directory_textbox.config(state=DISABLED)
            except:
                groups_textbox.config(state=NORMAL)
                groups_textbox.delete(0, END)
                groups_textbox.insert(0, "please choose file to save")
                groups_textbox.config(state=DISABLED)

def check_if_username_exist(username):
    net.send_flag("check username")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(username.encode())

        answer = net.net_socket.recv(100).decode()
        if(answer == "True"):
            return True
        return False

def check_if_email_exist(email):
    net.send_flag("check email")
    answer = net.net_socket.recv(15).decode()
    if (answer == "got flag"):
        net.net_socket.send(email.encode())

        answer = net.net_socket.recv(100).decode()
        if (answer == "True"):
            return True
        return False



def username_check_reg(username):
    if(len(username) > 16 or len(username)<6):
        return bool_and_string(False, "the username's len should be between 6 to 16")
    if(re.match(r"^[a-zA-Z0-9]+$",username) == None):
        return bool_and_string(False, "there are bad letters your username")
    if(check_if_username_exist(username)):
        return bool_and_string(False, "the username is already exist in the database")
    return bool_and_string(True, "")

def username_check_login(username):
    if(len(username) > 16 or len(username)<6):
        return bool_and_string(False, "the username's len should be between 6 to 16")
    if(re.match(r"^[a-zA-Z0-9]+$",username) == None):
        return bool_and_string(False, "there are bad letters your username")
    return bool_and_string(True, "")

def password_check(password):
    if (len(password) > 16 or len(password) < 6):
        return bool_and_string(False, "the password's len should be between 6 to 16")
    if (re.match(r"^[a-zA-Z0-9]+$", password) == None):
        return bool_and_string(False, "there are bad letters your password")
    return bool_and_string(True, "")

def re_password_check(password,re_password):
    if (len(re_password) > 16 or len(re_password) < 6):
        return bool_and_string(False, "the re_password's len should be between 6 to 16")
    if (re.match(r"^[a-zA-Z0-9]+$", re_password) == None):
        return bool_and_string(False, "there are bad letters your re_password")
    if(password != re_password):
        return  bool_and_string(False, "your passwords arent the same")
    return bool_and_string(True, "")

def email_check(email):
    if(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email) == None):
        return bool_and_string(False, "your email isnt valid")
    if(check_if_email_exist(email)):
        return bool_and_string(False, "the email is already exist in the database")
    return bool_and_string(True, "")

def first_check(first):
    flag = ""
    if (len(first) > 16 or len(first) < 2):
        return bool_and_string(False, "the first name's len should be between 2 to 16")
    if(re.match(r"^[a-zA-Z]+$", first) == None):
        return bool_and_string(False, "there are bad letters your first name")
    return bool_and_string(True, "")

def last_check(last):
    if (len(last) > 16 or len(last) < 2):
        return bool_and_string(False, "the last name's len should be between 2 to 16")
    if(re.match(r"^[a-zA-Z]+$", last) == None):
        return bool_and_string(False, "there are bad letters your last name")
    return bool_and_string(True, "")
def gender_check(gender):
    if(gender == ""):
        return bool_and_string(False, "choose your gender")
    return bool_and_string(True, "")

def mikum_check(mikum):
    if (mikum == ""):
        return bool_and_string(False, "choose your mikum")
    return bool_and_string(True, "")

def register_submit():
    global info_textbox_register
    info_textbox_register.delete(0, "end")

    global name_register_var
    global passw_register_var
    global re_passw_register_var
    global email_register_var
    global first_register_var
    global last_register_var
    global gender_register_var
    global mikum_register_var


    username = name_register_var.get()
    password = passw_register_var.get()
    re_password = re_passw_register_var.get()
    email = email_register_var.get()
    first = first_register_var.get()
    last = last_register_var.get()
    gender = gender_register_var.get()
    mikum = mikum_register_var.get()

    var_user = username_check_reg(username)
    var_password = password_check(password)
    var_re_password = re_password_check(password, re_password)
    var_email = email_check(email)
    var_first = first_check(first)
    var_last = last_check(last)
    var_gender = gender_check(gender)
    var_mikum = mikum_check(mikum)


    info_textbox_register.config(state="normal")
    info_textbox_register.delete(0, "end")

    if (var_first.GetFlag() == False):
        first_textbox.delete(0, "end")
        info_textbox_register.insert(0,var_first.GetText())

    elif (var_last.GetFlag() == False):
        last_textbox.delete(0, "end")
        info_textbox_register.insert(0,var_last.GetText())

    elif (var_gender.GetFlag() == False):
        info_textbox_register.insert(0,var_gender.GetText())

    elif (var_mikum.GetFlag() == False):
        info_textbox_register.insert(0,var_mikum.GetText())

    elif (var_user.GetFlag() == False):
        username_textbox.delete(0, "end")
        info_textbox_register.insert(0,var_user.GetText())

    elif (var_password.GetFlag() == False):
        password_textbox.delete(0, "end")
        info_textbox_register.insert(0,var_password.GetText())

    elif (var_re_password.GetFlag() == False):
        re_password_textbox.delete(0, "end")
        info_textbox_register.insert(0,var_re_password.GetText())

    elif (var_email.GetFlag() == False):
        email_textbox.delete(0, "end")
        info_textbox_register.insert(0,var_email.GetText())

    else:
        info_textbox_register.insert(0, "your info sent to the server")
        call_net_send_register(This_Client.net, first, last, gender, mikum, username, password, re_password, email)

        first_textbox.delete(0, "end")
        last_textbox.delete(0, "end")
        username_textbox.delete(0, "end")
        password_textbox.delete(0, "end")
        re_password_textbox.delete(0, "end")
        email_textbox.delete(0, "end")

        radio_male.deselect()
        radio_female.deselect()
        radio_center.deselect()
        radio_north.deselect()
        radio_south.deselect()


    info_textbox_register.config(state=DISABLED)


def login_submit():
    global info_textbox_login
    info_textbox_login.delete(0, "end")

    global name_login_var
    global passw_login_var

    username = name_login_var.get()
    password = passw_login_var.get()

    var_user = username_check_login(username)
    var_password = password_check(password)

    server_data = call_net_send_login(This_Client.net, username, password)

    info_textbox_login.config(state="normal")
    info_textbox_login.delete(0, "end")
    if(var_user.GetFlag() == False):
        info_textbox_login.insert(0,var_user.GetText())
    elif (var_password.GetFlag() == False):
        info_textbox_login.insert(0,var_password.GetText())
    elif(server_data.split(",")[0] == "False"):
        info_textbox_login.insert(0, "your user isnt exist")

    elif(server_data == "the user is already connected"):
        info_textbox_login.insert(0, server_data)

    info_textbox_login.config(state=DISABLED)

    if(server_data.split(",")[0] == "True"):
        info_textbox_login.insert(0, "you logged in succssesfully")
        info_textbox_login.config(state=DISABLED)
        print("user: " + username)
        print("password: " + password)
        This_Client.user = user(server_data.split(",")[1], server_data.split(",")[2], server_data.split(",")[3],  server_data.split(",")[4], server_data.split(",")[5], server_data.split(",")[6], server_data.split(",")[7], server_data.split(",")[8])
        sending_page()



def create_frame():
    example = tk.Frame(bg=_from_rgb((255,255,255)))
    example.pack(fill='both', expand=True)
    example.bind('<Configure>', "1600x900")
    global frame_default
    frame_default = example
    return example

def create_file_alert_window(filename, file_object):
    global win
    win = tk.Toplevel()
    win.configure(bg="white")
    win.geometry("500x300+125+75")
    win.resizable(False, False)
    win.grab_set()
    alert_frame = tk.Frame(win)
    alert_frame.pack(fill='both', expand=True)
    alert_frame.bind('<Configure>', "500x400")
    write(alert_frame, "beware!", 0.2)

    alert_text = tk.Label(alert_frame,
                             text="the file you are trying to upload is already",
                             fg=button_bg_color,
                             font="calibri 12",
                                bg="white"
                             )
    alert_text.pack()
    alert_text.place(relx=0.165, rely=0.35)

    alert_text2 = tk.Label(alert_frame,
                          text="exist in the database",
                          fg=button_bg_color,
                          font="calibri 12",
                                bg="white"
                          )
    alert_text2.pack()
    alert_text2.place(relx=0.33, rely=0.425)

    alert_text3 = tk.Label(alert_frame,
                           text="do you want to override the file",
                           fg=button_bg_color,
                           font="calibri 12",
                                bg="white"
                           )
    alert_text3.pack()
    alert_text3.place(relx=0.245, rely=0.5)

    alert_text4 = tk.Label(alert_frame,
                           text="or upload it with the name",
                           fg=button_bg_color,
                           font="calibri 12",
                                bg="white"
                           )
    alert_text4.pack()
    alert_text4.place(relx=0.29, rely=0.575)

    alert_text5 = tk.Label(alert_frame,
                           text=filename + "?",
                           fg=button_bg_color,
                           font="calibri 12",
                                bg="white"
                           )
    alert_text5.pack()
    alert_text5.place(relx=0.425, rely=0.65)
    global current_group_shown
    override_button = tk.Button(alert_frame, text="override", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=6, command=lambda:threaded_func(call_net_send_and_delete_file, (This_Client.net, file_object)))
    override_button['font'] = myFont
    override_button.pack()
    override_button.place(relx=0.1, rely=0.75)


    override_button = tk.Button(alert_frame, text="change", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=6, command=lambda:threaded_func(call_net_send_file,(This_Client.net, get_path(), True, filename, current_group_shown)))
    override_button['font'] = myFont
    override_button.pack()
    override_button.place(relx=0.6, rely=0.75)



    "filename = filename"

def disconnect_user():
    net.send_flag("disconnect user")
    answer = net.net_socket.recv(4069).decode()
    if(answer == "got flag"):
        print(This_Client.user.username)
        net.net_socket.send(This_Client.user.username.encode())
    home_page("disconnected")

def disconnect_user2():
    net.send_flag("disconnect user")
    answer = net.net_socket.recv(4069).decode()
    if (answer == "got flag"):
        print(This_Client.user.username)
        net.net_socket.send(This_Client.user.username.encode())

def home_page(state):
    if(state == "disconnected"):
        This_Client.user = None

    frame_default.destroy()
    frame_home_page = create_frame()

    myFont = font.Font(size=30, family="calibri")

    logo_img_label = tk.Label(frame_home_page, image=logo_img, borderwidth=0, bg="white")
    logo_img_label.pack()
    logo_img_label.place(relx=0.18, rely=-0.225)

    button_login = tk.Button(frame_home_page, text="login", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, activeforeground="white",  height=2, width=10, command=lambda:threaded_func(login, None))
    button_login['font'] = myFont
    button_login.pack()
    button_login.place(relx=0.75, rely=0.6)

    button_register = tk.Button(frame_home_page, text="register", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, activeforeground="white",  height=2, width=10, command=lambda:threaded_func(register, None))
    button_register['font'] = myFont
    button_register.pack()
    button_register.place(relx=0.1, rely=0.6)

def update():
    global txt_filename
    global textBox
    global text_index
    global txt_file_object

    with open(txt_filename + '.txt', 'w') as f:
        f.seek(0)
        f.write(textBox.get("0.0", "end-1c"))
    call_net_replace_txt_file(This_Client.net, txt_file_object)
    print(textBox.get("0.0", "end-1c"))

def alertme(*args):
    global txt_filename
    global textBox
    global text_index
    global txt_file_object
    text_index = text_index + 1
    if text_index > 2:
        with open(txt_filename + '.txt', 'w') as f:
            f.seek(0)
            f.write(textBox.get("0.0", "end-1c"))
        call_net_replace_txt_file(This_Client.net, txt_file_object)
        print(textBox.get("0.0", "end-1c"))
        text_index = 1

def override_every_five_seconds():
    while(True):
        time.sleep(5)
        with open(txt_filename + '.txt', 'w') as f:
            f.seek(0)
            f.write(textBox.get("0.0", "end-1c"))
        call_net_replace_txt_file(This_Client.net, txt_file_object)
        print(textBox.get("0.0", "end-1c"))



def txt_file_write_page(txt_file_bytes, file_object):
    global txt_file_object
    global txt_filename
    txt_file_object = file_object
    txt_filename = file_object.file
    frame_default.destroy()
    frame_text_file = create_frame()
    write(frame_text_file, "text file", 0.436)

    button_return_to_home_page = tk.Button(frame_text_file, text="disconnect", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=12,
                                           command=lambda: threaded_func(disconnect_user, None))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=75, y=50)

    user_first_text = tk.Label(frame_text_file,
                               text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                               fg=button_bg_color,
                               font="calibri 25 bold underline",
                               bg="white"
                               )
    user_first_text.pack()
    user_first_text.place(relx=0.75, rely=0.2)

    request_image_button = tk.Button(frame_text_file, text="request page", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=12,
                                     command=lambda: threaded_func(request_page, None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=150)

    button_update = tk.Button(frame_text_file, text="update", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=2, width=10, command=lambda:threaded_func(update, None))
    button_update['font'] = myFont
    button_update.pack()
    button_update.place(relx=0.425, rely=0.6)

    global text_index
    text_index = 1

    global textBox
    textBox = Text(frame_text_file, height=15, width=60)
    textBox.pack()
    textBox.place(relx=0.35, rely=0.1)

    with open(file_object.file + '.txt', 'wb') as txt_file:
        txt_file.seek(0)
        txt_file.write(txt_file_bytes)

    with open(file_object.file + '.txt', 'r') as txt_file:
        txt_file.seek(0)
        data = txt_file.readlines()
    for line in data:
        textBox.insert(INSERT, line)

    #txt_thread = threading.Thread(target=override_every_five_seconds())
    #txt_thread.start()

    textBox.bind('<KeyRelease>', alertme)





def login():
    global name_login_var
    global passw_login_var
    name_login_var = tk.StringVar()
    passw_login_var = tk.StringVar()

    frame_default.destroy()
    frame_login = create_frame()
    write(frame_login, "login", 0.436)

    button_return_to_home_page = tk.Button(frame_login, text="home page", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=10, command=lambda:threaded_func(home_page, ("connect",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=100, y=50)


    username_text = tk.Label(frame_login,
                    text="username:",
                    fg=button_bg_color,
                    font="calibri 25 bold underline",
                    bg="white"
                    )
    username_text.pack()
    username_text.place(relx=0.355, rely=0.25)

    username_textbox = Entry(frame_login,textvariable = name_login_var , width=27)
    username_textbox.pack()
    username_textbox.place(relx=0.5175, rely=0.27)

    password_text = tk.Label(frame_login,
                    text="password:",
                    fg=button_bg_color,
                    font="calibri 25 bold underline",
                    bg="white"
                    )
    password_text.pack()
    password_text.place(relx=0.355, rely=0.45)

    password_textbox = Entry(frame_login,textvariable = passw_login_var ,show="*", width=27)
    password_textbox.pack()
    password_textbox.place(relx=0.5175, rely=0.47)

    submit_button = tk.Button(frame_login, text="submit", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=7, command = lambda:threaded_func(login_submit, None))
    submit_button['font'] = myFont
    submit_button.pack(pady=10)
    submit_button.place(relx=0.4475, rely=0.675)

    global info_textbox_login
    info_textbox_login = Entry(frame_login, width=50)
    info_textbox_login.pack()
    info_textbox_login.place(relx=0.40125, rely=0.825)
    info_textbox_login.delete(0, "end")
    info_textbox_login.config(state=DISABLED)


def register():

    global name_register_var
    global passw_register_var
    global first_register_var
    global last_register_var
    global re_passw_register_var
    global email_register_var
    global gender_register_var
    global mikum_register_var
    name_register_var = tk.StringVar()
    passw_register_var = tk.StringVar()
    first_register_var = tk.StringVar()
    last_register_var = tk.StringVar()
    re_passw_register_var = tk.StringVar()
    email_register_var = tk.StringVar()
    gender_register_var = tk.StringVar()
    mikum_register_var = tk.StringVar()


    frame_default.destroy()
    frame_register = create_frame()
    write(frame_register, "register", 0.425)

    global info_textbox_register
    info_textbox_register = Entry(frame_register, width=50)
    info_textbox_register.pack(side=BOTTOM, pady=20)
    info_textbox_register.place(relx=0.4, rely=0.95)
    info_textbox_register.delete(0, "end")
    info_textbox_register.config(state=DISABLED)

    button_return_to_home_page = tk.Button(frame_register, text="home page", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=10, command=lambda:threaded_func(home_page, ("connect",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(side=LEFT, pady=10)
    button_return_to_home_page.place(x=100, y=50)

    first_text = tk.Label(frame_register,
                             text="first name:",
                             fg=button_bg_color,
                             font="calibri 25 bold underline",
                                bg="white"

                             )
    first_text.pack()
    first_text.place(relx=0.345, rely=0.2)

    global first_textbox
    first_textbox = Entry(frame_register, textvariable=first_register_var, width=27)
    first_textbox.pack(side=LEFT, padx=100)
    first_textbox.place(relx=0.555, rely=0.22)

    last_text = tk.Label(frame_register,
                             text="last name:",
                             fg=button_bg_color,
                             font="calibri 25 bold underline",
                                bg="white"
                             )
    last_text.pack(side=LEFT, padx=100)
    last_text.place(relx=0.345, rely=0.275)

    global last_textbox
    last_textbox = Entry(frame_register, textvariable=last_register_var, width=27)
    last_textbox.pack(side=LEFT, padx=100)
    last_textbox.place(relx=0.555, rely=0.295)

    gender_text = tk.Label(frame_register,
                         text="gender:",
                         fg=button_bg_color,
                         font="calibri 25 bold underline",
                         bg="white"
                         )
    gender_text.pack(side=LEFT, padx=100)
    gender_text.place(relx=0.345, rely=0.35)

    global radio_male
    radio_male = Radiobutton(frame_register, text="male", bg="white", variable=gender_register_var, value="male", tristatevalue="default")
    radio_male.pack(anchor = tk.W)
    radio_male.place(relx=0.555, rely=0.37)

    global radio_female
    radio_female = Radiobutton(frame_register, text="female", bg="white", variable=gender_register_var, value="female", tristatevalue="default")
    radio_female.pack(anchor = tk.W)
    radio_female.place(relx=0.615, rely=0.37)

    mikum_text = tk.Label(frame_register,
                           text="mikum:",
                           fg=button_bg_color,
                           font="calibri 25 bold underline",
                                bg="white"
                           )
    mikum_text.pack(side=LEFT, padx=100)
    mikum_text.place(relx=0.345, rely=0.425)

    global radio_center
    radio_center = Radiobutton(frame_register, text="center", bg="white", variable=mikum_register_var, value="center",
                             tristatevalue="default")
    radio_center.pack(anchor=tk.W)
    radio_center.place(relx=0.525, rely=0.445)

    global radio_north
    radio_north = Radiobutton(frame_register, text="north", bg="white", variable=mikum_register_var, value="north",
                               tristatevalue="default")
    radio_north.pack(anchor=tk.W)
    radio_north.place(relx=0.595, rely=0.445)

    global radio_south
    radio_south = Radiobutton(frame_register, text="south", bg="white", variable=mikum_register_var, value="south",
                               tristatevalue="default")
    radio_south.pack(anchor=tk.W)
    radio_south.place(relx=0.665, rely=0.445)







    username_text = tk.Label(frame_register,
                    text="username:",
                    fg=button_bg_color,
                    font="calibri 25 bold underline",
                                bg="white"
                    )
    username_text.pack()
    username_text.place(relx=0.345, rely=0.5)

    global username_textbox
    username_textbox = Entry(frame_register, textvariable = name_register_var , width=27)
    username_textbox.pack()
    username_textbox.place(relx=0.555,rely=0.52)

    password_text = tk.Label(frame_register,
                    text="password:",
                    fg=button_bg_color,
                    font="calibri 25 bold underline",
                                bg="white"
                    )
    password_text.pack()
    password_text.place(relx=0.345, rely=0.575)

    global password_textbox
    password_textbox = Entry(frame_register,textvariable = passw_register_var ,show="*", width=27)
    password_textbox.pack()
    password_textbox.place(relx=0.555, rely=0.595)

    re_password_text = tk.Label(frame_register,
                             text="re-password:",
                             fg=button_bg_color,
                             font="calibri 25 bold underline",
                                bg="white"
                             )
    re_password_text.pack()
    re_password_text.place(relx=0.345, rely=0.65)

    global re_password_textbox
    re_password_textbox = Entry(frame_register, textvariable=re_passw_register_var, show="*", width=27)
    re_password_textbox.pack()
    re_password_textbox.place(relx=0.555, rely=0.67)

    email_text = tk.Label(frame_register,
                                text="email:",
                                fg=button_bg_color,
                                font="calibri 25 bold underline",
                                bg="white"
                                )
    email_text.pack()
    email_text.place(relx=0.345, rely=0.725)

    global email_textbox
    email_textbox = Entry(frame_register, textvariable=email_register_var, width=27)
    email_textbox.pack()
    email_textbox.place(relx=0.555, rely=0.745)



    """submit button"""

    submit_register_button = tk.Button(frame_register, text="register", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=7, command=lambda:threaded_func(register_submit, None))
    submit_register_button['font'] = myFont
    submit_register_button.pack(pady=10)
    submit_register_button.place(relx=0.445, rely=0.8)

def groups_page():
    global current_group_shown
    current_group_shown = "Null"
    frame_default.destroy()
    global frame_groups
    frame_groups = create_frame()
    write(frame_groups, "groups page", 0.37)

    user_first_text = tk.Label(frame_groups,
                               text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                               fg=button_bg_color,
                               font="calibri 25 bold underline",
                                bg="white"
                               )
    user_first_text.pack()
    user_first_text.place(relx=0.75, rely=0.2)

    button_return_to_home_page = tk.Button(frame_groups, text="disconnect", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                           command=lambda: threaded_func(disconnect_user, None))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=75, y=50)

    request_image_button = tk.Button(frame_groups, text="sending page", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                     command=lambda: threaded_func(sending_page, None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=150)

    request_image_button = tk.Button(frame_groups, text="request page", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                     command=lambda: threaded_func(request_page, None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=250)

    your_groups_text = tk.Label(frame_groups,
                               text="your groups",
                               fg=button_bg_color,
                               font="calibri 32 underline",
                                bg="white"
                               )
    your_groups_text.pack()
    your_groups_text.place(relx=0.0525, rely=0.385)

    users_group = call_net_get_users_groups()
    global groups_lb
    groups_lb = create_users_group_listbox(users_group)
    groups_lb.pack()
    groups_lb.place(relx=0.0525, rely=0.485)
    groups_lb.bind('<<ListboxSelect>>', groups_onselect)

    global users_lb
    users_lb = create_users_listbox()
    users_lb.pack()
    users_lb.place(relx=0.76, rely=0.3)
    users_lb.bind('<<ListboxSelect>>', users_onselect)

    global groups_listbox_var
    show_group_button = tk.Button(frame_groups, text="show", height=1, width=5, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, command=lambda:threaded_func(show_group_data,(groups_listbox_var,)))
    show_group_button['font'] = myFont
    show_group_button.pack(pady=10)
    show_group_button.place(relx=0.0425, rely=0.65)

    reset_group_page_button = tk.Button(frame_groups, text="reset", height=1, width=5, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, command=lambda: threaded_func(groups_page, None))
    reset_group_page_button['font'] = myFont
    reset_group_page_button.pack(pady=10)
    reset_group_page_button.place(relx=0.1245, rely=0.65)

    create_group_page_button = tk.Button(frame_groups, text="create group", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, command=lambda:threaded_func(create_group_win, None))
    create_group_page_button['font'] = myFont
    create_group_page_button.pack(pady=10)
    create_group_page_button.place(relx=0.0435, rely=0.75)

    join_group_page_button = tk.Button(frame_groups, text="join group", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, command=lambda:threaded_func(join_group_win, None))
    join_group_page_button['font'] = myFont
    join_group_page_button.pack(pady=10)
    join_group_page_button.place(relx=0.0435, rely=0.85)

    global is_selected
    is_selected = "unselected"
    file_sending_button = tk.Button(frame_groups, text="choose file", height=1, width=9, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                    command=lambda: threaded_func(choose_file_to_send, (is_selected,)))
    file_sending_button['font'] = myFont
    file_sending_button.pack(pady=10)
    file_sending_button.place(relx=0.425, rely=0.6)

    global groups_textbox
    groups_textbox = Entry(frame_groups, width=40)
    groups_textbox.pack()
    groups_textbox.place(relx=0.408, rely=0.9)
    groups_textbox.config(state=DISABLED)

    global groups_filename_textbox
    groups_filename_textbox = Entry(frame_groups, textvariable=path, width=31)
    groups_filename_textbox.pack()
    groups_filename_textbox.place(relx=0.425, rely=0.86)

    button_send_image = tk.Button(frame_groups, text="send image", height=1, width=9, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                  command=lambda: threaded_func(group_send_file, None))
    button_send_image['font'] = myFont
    button_send_image.pack()
    button_send_image.place(relx=0.425, rely=0.75)
    groups_filename_textbox.config(state=DISABLED)

    create_group_file_listbox()


    get_file_button = tk.Button(frame_groups, text="get file", height=1, width=9, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                command=lambda: threaded_func(call_net_request_file_and_open, (fix_group_files_listbox_var(files_listbox_var), current_group_shown)))
    get_file_button['font'] = myFont
    get_file_button.pack(pady=10)
    get_file_button.place(relx=0.625, rely=0.6)

    delete_file_button = tk.Button(frame_groups, text="delete file", height=1, width=9, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                   command=lambda: threaded_func(delete_group_file, (files_listbox_var,)))
    delete_file_button['font'] = myFont
    delete_file_button.pack(pady=10)
    delete_file_button.place(relx=0.625, rely=0.7)

    save_file_button = tk.Button(frame_groups, text="save file", height=1, width=9, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                 command=lambda: threaded_func(call_net_request_file_and_save, (fix_group_files_listbox_var(files_listbox_var), current_group_shown)))
    save_file_button['font'] = myFont
    save_file_button.pack(pady=10)
    save_file_button.place(relx=0.625, rely=0.8)

def request_page():
    global search_var
    search_var = tk.StringVar()
    global requested_filename_var
    requested_filename_var = tk.StringVar()

    frame_default.destroy()
    global frame_request
    frame_request = create_frame()
    write(frame_request, "request page", 0.345)

    global search_textbox
    search_textbox = Entry(frame_request, width=20, textvariable=search_var)
    search_textbox.pack()
    search_textbox.place(relx=0.39, rely=0.25)
    search_textbox.configure(font=("calibri", 22))

    arr_of_filenames = get_user_filenames(This_Client.user.username)
    create_listbox("not destroy", arr_of_filenames)

    user_first_text = tk.Label(frame_request,
                               text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                               fg=button_bg_color,
                               font="calibri 25 bold underline",
                                bg="white"
                               )
    user_first_text.pack()
    user_first_text.place(relx=0.75, rely=0.2)

    files_text = tk.Label(frame_request,
                          text="files:",
                          fg=button_bg_color,
                          font="calibri 35 bold underline",
                                bg="white"
                          )
    files_text.pack()
    files_text.place(relx=0.46, rely=0.1)



    search_text = tk.Label(frame_request,
                          text="search:",
                          fg=button_bg_color,
                          font="calibri 25 bold underline",
                                bg="white"
                          )
    search_text.pack()
    search_text.place(relx=0.459, rely=0.175)

    search_button = tk.Button(frame_request, text="search", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=5, command=lambda:threaded_func(create_specific_listbox, None))
    search_button['font'] = myFont
    search_button.pack(pady=10)
    search_button.place(relx=0.4, rely=0.3)

    reset_button = tk.Button(frame_request, text="reset", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=5, command=lambda:threaded_func(create_listbox, ("destroy", arr_of_filenames)))
    reset_button['font'] = myFont
    reset_button.pack(pady=10)
    reset_button.place(relx=0.53, rely=0.3)

    get_file_button = tk.Button(frame_request, text="get file", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=7, command=lambda:threaded_func(call_net_request_file_and_open, (listbox_var, "Null")))
    get_file_button['font'] = myFont
    get_file_button.pack(pady=10)
    get_file_button.place(relx=0.625, rely=0.8)

    delete_file_button = tk.Button(frame_request, text="delete file", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=7, command=lambda:threaded_func(delete_file, (listbox_var,)))
    delete_file_button['font'] = myFont
    delete_file_button.pack(pady=10)
    delete_file_button.place(relx=0.3, rely=0.8)

    save_file_button = tk.Button(frame_request, text="save file", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=7, command=lambda:threaded_func(call_net_request_file_and_save, (listbox_var, "Null")))
    save_file_button['font'] = myFont
    save_file_button.pack(pady=10)
    save_file_button.place(relx=0.4625, rely=0.8)

    global directory_textbox
    directory_textbox = Entry(frame_request, width=28)
    directory_textbox.pack()
    directory_textbox.place(relx=0.4625, rely=0.75)
    directory_textbox.config(state=DISABLED)



    button_return_to_home_page = tk.Button(frame_request, text="disconnect", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                           command=lambda:threaded_func(disconnect_user, None))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=75, y=50)

    request_image_button = tk.Button(frame_request, text="sending page", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=12, command=lambda:threaded_func(sending_page, None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=150)

    groups_page_button = tk.Button(frame_request, text="groups page", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=12,
                                   command=lambda: threaded_func(groups_page, None))
    groups_page_button['font'] = myFont
    groups_page_button.pack(pady=10)
    groups_page_button.place(x=75, y=250)








def sending_page():
    global current_group_shown
    current_group_shown = "Null"
    global db_answer_textbox
    global path
    path = tk.StringVar()
    frame_default.destroy()
    frame_sending = create_frame()
    write(frame_sending, "sending page", 0.4)

    user_first_text = tk.Label(frame_sending,
                             text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                             fg=button_text_color,
                             font="calibri 25 bold underline",
                             bg="white"
                             )
    user_first_text.pack()
    user_first_text.place(relx=0.7, rely=0.3)

    file_sending_button = tk.Button(frame_sending, text="choose file", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=9, command=lambda:threaded_func(choose_file_to_send, ("selected",)))
    file_sending_button['font'] = myFont
    file_sending_button.pack(pady=10)
    file_sending_button.place(relx=0.45, rely=0.4)

    global filename_textbox
    filename_textbox = Entry(frame_sending, textvariable=path, width=32)
    filename_textbox.pack()
    filename_textbox.place(relx=0.45, rely=0.6)


    button_send_image = tk.Button(frame_sending, text="send image", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=9,
                                  command=lambda:threaded_func(call_net_send_file, (This_Client.net, get_path(), False, "", "Null")))
    button_send_image['font'] = myFont
    button_send_image.pack()
    button_send_image.place(relx=0.45, rely=0.7)
    filename_textbox.config(state=DISABLED)

    button_return_to_home_page = tk.Button(frame_sending, text="disconnect", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=12, command=lambda:threaded_func(disconnect_user, None))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=75, y=50)

    request_image_button = tk.Button(frame_sending, text="request page", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, height=1, width=12, command=lambda:threaded_func(request_page, None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=150)

    groups_page_button = tk.Button(frame_sending, text="groups page", height=1, width=12, bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color,
                                     command=lambda: threaded_func(groups_page, None))
    groups_page_button['font'] = myFont
    groups_page_button.pack(pady=10)
    groups_page_button.place(x=75, y=250)

    db_answer_textbox = Entry(frame_sending, width=40)
    db_answer_textbox.pack()
    db_answer_textbox.place(relx=0.4375, rely=0.85)
    db_answer_textbox.config(state=DISABLED)


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

def write(frame, text, x):
    text = tk.Label(frame,
    text=text,
    fg=button_bg_color,
    font="calibri 50 bold underline",
    bg="white"
    )
    text.pack(side=TOP, pady=50)
    text.place(relx=x)


net = network()
net.connect_to_server()
This_Client = client(net, None)


root = tk.Tk()
root.state("zoomed")
frame_default = tk.Frame(bg=_from_rgb((255,255,255)))
frame_default.pack(fill='both', expand=True)
frame_default.bind('<Configure>', "1600x900")

button_text_color = "white"
button_bg_color = _from_rgb((0,87,146))
button_clicked_color = _from_rgb((0,72,146))
listbox_color = _from_rgb((0,105,146))

logo_img = Image.open("logo.png")
logo_img = logo_img.resize((1000, 600))
logo_img = ImageTk.PhotoImage(logo_img)

logo_img_label = tk.Label(frame_default, image=logo_img, borderwidth=0)
logo_img_label.pack()
logo_img_label.place(relx=0.18, rely=-0.225)


myFont = font.Font(size=30, family="calibri")
button_login = tk.Button(frame_default, text="LOGIN", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, activeforeground="white", height=2, width=10, command=lambda:threaded_func(login, None))
button_login['font'] = myFont
button_login.pack()
button_login.place(relx=0.75, rely=0.6)


button_register = tk.Button(frame_default, text="REGISTER", bg=button_bg_color, fg=button_text_color, activebackground=button_clicked_color, activeforeground="white", height=2, width=10, command=lambda:threaded_func(register, None))
button_register['font'] = myFont
button_register.pack()
button_register.place(relx=0.1, rely=0.6)


root.geometry("1600x900+125+75")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()



