import threading
import tkinter as tk
import tkinter.font as font
from tkinter import *
from tkinter import filedialog as fd
import pickle
from PIL import ImageFile, Image
import os
import socket
import re
from MyClasses import user, client, network, bool_and_string, file, username_and_filename
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
    This_Client.user = None
    This_Client.net.net_socket.close()
    root.destroy()

def choose_file_to_send():
    global filename_textbox
    filename_textbox.config(state="normal")
    filename_textbox.delete(0, "end")
    global filename
    filename = fd.askopenfilename(title='choose a file', initialdir='/')
    print(filename)
    if(str(filename) == ""):
        filename_textbox.insert(0, "please choose path")
        filename_textbox.config(state=DISABLED)
    else:
        filename_textbox.insert(0, str(filename).split("/")[len(str(filename).split("/"))-1])
        filename_textbox.config(state=DISABLED)

def choose_where_to_save():
    global directory_textbox
    directory_textbox.config(state="normal")
    directory_textbox.delete(0, "end")
    global directory
    directory = fd.askdirectory(title='choose a directory', initialdir='/')
    if(str(directory) == ""):
        directory_textbox.insert(0, "please choose directory")
        directory_textbox.config(state=DISABLED)
    return directory

def get_path():
    global path
    return path.get()

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


def create_listbox(flag, arr_of_filenames):
    global listbox

    global search_textbox
    search_textbox.delete(0, END)

    if(flag == "destroy"):
        listbox.destroy()

    listbox = Listbox(frame_request, height=4,
                      width=16,
                      bg="grey",
                      activestyle='dotbox',
                      font=("Verdana", 36),
                      fg="white")
    listbox.bind('<<ListboxSelect>>', onselect)

    index = 1
    while (index < len(arr_of_filenames) + 1):
        listbox.insert(index, arr_of_filenames[index - 1])
        index = index + 1
    listbox.pack()
    listbox.place(relx=0.35, rely=0.4)

    global listbox_var
    listbox_var = ""

def call_net_send_and_delete_file(net, file_object):
    global win
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

def call_net_send_file(net, path, resend_flag, fixed_filename):
    if(path != "" and path != "please choose path"):
        global filename
        global db_answer_textbox

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
        file_object = file(This_Client.user.username, file_name3, type, size)
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
                    db_answer_textbox.config(state=NORMAL)
                    db_answer_textbox.delete(0, END)
                    db_answer_textbox.insert(0, db_answer)
                    db_answer_textbox.config(state=DISABLED)
                else:
                    create_file_alert_window(db_answer, file_object)
            else:
                global win
                win.destroy()



def listbox_of_filenames(arr):
    listbox = Listbox(frame_default, height=4,
                      width=15,
                      bg="grey",
                      activestyle='dotbox',
                      font=("Courier", 44),
                      fg="white")
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

def delete_file(value):
    global listbox
    if (value == listbox.get(ANCHOR)):
        listbox.delete(ANCHOR)

        delete_object = username_and_filename(This_Client.user.username, value)

        net.send_flag("delete file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            net.net_socket.send(pickle.dumps(delete_object, 0))




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

def call_net_request_file_and_open(requested_filename):
    if(requested_filename != ""):
        net.send_flag("request file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            requested_filename_with_type = requested_filename
            mini_arr = requested_filename.split(".")
            mini_arr.pop()
            requested_filename = ".".join(mini_arr)
            net.send_request_file_data(This_Client.user.username, requested_filename)

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

                    #os.remove(requested_file_object.file + '.docx')

                else:
                    file_arr = io.BytesIO(requested_file_bytes)
                    opened_file = Image.open(file_arr)
                    opened_file.show()



            else:
                print("no match")

        else:
            print("no match")


def call_net_request_file_and_save(requested_filename):
    global directory_textbox
    if(requested_filename != ""):
        requested_filename_with_type =requested_filename
        net.send_flag("request file")
        answer = net.net_socket.recv(15).decode()
        if (answer == "got flag"):
            mini_arr = requested_filename.split(".")
            mini_arr.pop()
            requested_filename = ".".join(mini_arr)
            net.send_request_file_data(This_Client.user.username, requested_filename)

            mini_flag = str(net.net_socket.recv(100).decode())
            if(mini_flag == "found image"):
                rcv_object = net.net_socket.recv(500)
                requested_file_object = pickle.loads(rcv_object)

                requested_file_bytes = b""
                requested_file_bytes += net.net_socket.recv(int(requested_file_object.size))

                directory_path = os.path.abspath(choose_where_to_save())
                file_path = os.path.abspath(directory_path + "/" + requested_filename_with_type)
                print(file_path)
                with open(file_path, 'wb') as file:
                    file.seek(0)
                    file.write(requested_file_bytes)
                directory_textbox.config(state=NORMAL)
                directory_textbox.delete(0, END)
                directory_textbox.insert(0, "your file saved succssesfully")
                directory_textbox.config(state=DISABLED)


            else:
                directory_textbox.config(state=NORMAL)
                directory_textbox.delete(0, END)
                directory_textbox.insert(0, "please choose file to save")
                directory_textbox.config(state=DISABLED)

        else:
            directory_textbox.config(state=NORMAL)
            directory_textbox.delete(0, END)
            directory_textbox.insert(0, "please choose file to save")
            directory_textbox.config(state=DISABLED)

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



def username_check(username):
    if(len(username) > 16 or len(username)<6):
        return bool_and_string(False, "the username's len should be between 6 to 16")
    if(re.match(r"^[a-zA-Z0-9]+$",username) == None):
        return bool_and_string(False, "there are bad letters your username")
    if(check_if_username_exist(username)):
        return bool_and_string(False, "the username is already exist in the database")
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

    var_user = username_check(username)
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

    var_user = username_check(username)
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

    info_textbox_login.config(state=DISABLED)

    if(server_data.split(",")[0] == "True"):
        info_textbox_login.insert(0, "you logged in succssesfully")
        info_textbox_login.config(state=DISABLED)
        print("user: " + username)
        print("password: " + password)
        This_Client.user = user(server_data.split(",")[1], server_data.split(",")[2], server_data.split(",")[3],  server_data.split(",")[4], server_data.split(",")[5], server_data.split(",")[6], server_data.split(",")[7], server_data.split(",")[8])
        sending_page()


def create_frame():
    example = tk.Frame()
    example.pack(fill='both', expand=True)
    example.bind('<Configure>', "1600x900")
    global frame_default
    frame_default = example
    return example

def create_file_alert_window(filename, file_object):
    global win
    win = tk.Toplevel()
    win.geometry("500x300+125+75")
    win.resizable(False, False)
    win.grab_set()
    alert_frame = tk.Frame(win)
    alert_frame.pack(fill='both', expand=True)
    alert_frame.bind('<Configure>', "500x400")
    write(alert_frame, "beware!", 0.2)

    alert_text = tk.Label(alert_frame,
                             text="the file you are trying to upload is already",
                             fg="black",
                             font="Verdana 12"
                             )
    alert_text.pack()
    alert_text.place(relx=0.165, rely=0.35)

    alert_text2 = tk.Label(alert_frame,
                          text="exist in the database",
                          fg="black",
                          font="Verdana 12"
                          )
    alert_text2.pack()
    alert_text2.place(relx=0.33, rely=0.425)

    alert_text3 = tk.Label(alert_frame,
                           text="do you want to override the file",
                           fg="black",
                           font="Verdana 12"
                           )
    alert_text3.pack()
    alert_text3.place(relx=0.245, rely=0.5)

    alert_text4 = tk.Label(alert_frame,
                           text="or upload it with the name",
                           fg="black",
                           font="Verdana 12"
                           )
    alert_text4.pack()
    alert_text4.place(relx=0.29, rely=0.575)

    alert_text5 = tk.Label(alert_frame,
                           text=filename + "?",
                           fg="black",
                           font="Verdana 12"
                           )
    alert_text5.pack()
    alert_text5.place(relx=0.425, rely=0.65)

    override_button = tk.Button(alert_frame, text="override", height=1, width=6, command=lambda:threaded_func(call_net_send_and_delete_file, (This_Client.net, file_object)))
    override_button['font'] = myFont
    override_button.pack()
    override_button.place(relx=0.1, rely=0.75)

    override_button = tk.Button(alert_frame, text="change", height=1, width=6, command=lambda:threaded_func(call_net_send_file,(This_Client.net, get_path(), True, filename)))
    override_button['font'] = myFont
    override_button.pack()
    override_button.place(relx=0.6, rely=0.75)



    "filename = filename"


def home_page(state):
    if(state == "disconnected"):
        This_Client.user = None

    frame_default.destroy()
    frame_home_page = create_frame()
    write(frame_home_page, "UrCloud", 0.4)

    myFont = font.Font(size=30)

    button_login = tk.Button(frame_default, text="login", height=2, width=10, command=lambda:threaded_func(login, None))
    button_login['font'] = myFont
    button_login.pack()
    button_login.place(relx=0.75, rely=0.6)

    button_register = tk.Button(frame_default, text="register", height=2, width=10, command=lambda:threaded_func(register, None))
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
        print("baranes1")
        with open(txt_filename + '.txt', 'w') as f:
            f.seek(0)
            f.write(textBox.get("0.0", "end-1c"))
        print("baranes2")
        call_net_replace_txt_file(This_Client.net, txt_file_object)
        print("baranes69")
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

    button_return_to_home_page = tk.Button(frame_text_file, text="disconnect", height=1, width=10,
                                           command=lambda: threaded_func(home_page, ("disconnected",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=100, y=50)

    user_first_text = tk.Label(frame_text_file,
                               text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                               fg="black",
                               font="Verdana 25 bold underline"
                               )
    user_first_text.pack()
    user_first_text.place(relx=0.75, rely=0.2)

    sending_button = tk.Button(frame_text_file, text="sending page", height=1, width=12, command=lambda:threaded_func(sending_page, None))
    sending_button['font'] = myFont
    sending_button.pack(pady=10)
    sending_button.place(x=75, y=150)

    button_update = tk.Button(frame_text_file, text="update", height=2, width=10, command=lambda:threaded_func(update, None))
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

    button_return_to_home_page = tk.Button(frame_login, text="home page", height=1, width=10, command=lambda:threaded_func(home_page, ("connect",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=100, y=50)


    username_text = tk.Label(frame_login,
                    text="username:",
                    fg="black",
                    font="Verdana 25 bold underline"
                    )
    username_text.pack()
    username_text.place(relx=0.435, rely=0.25)

    username_textbox = Entry(frame_login,textvariable = name_login_var , width=27)
    username_textbox.pack()
    username_textbox.place(relx=0.4475, rely=0.375)

    password_text = tk.Label(frame_login,
                    text="password:",
                    fg="black",
                    font="Verdana 25 bold underline"
                    )
    password_text.pack()
    password_text.place(relx=0.435, rely=0.45)

    password_textbox = Entry(frame_login,textvariable = passw_login_var ,show="*", width=27)
    password_textbox.pack()
    password_textbox.place(relx=0.4475, rely=0.575)

    submit_button = tk.Button(frame_login, text="submit", height=1, width=7, command = lambda:threaded_func(login_submit, None))
    submit_button['font'] = myFont
    submit_button.pack(pady=10)
    submit_button.place(relx=0.4475, rely=0.675)

    global info_textbox_login
    info_textbox_login = Entry(frame_login, width=50)
    info_textbox_login.pack()
    info_textbox_login.place(relx=0.4, rely=0.825)
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
    write(frame_register, "register", 0.4)

    global info_textbox_register
    info_textbox_register = Entry(frame_register, width=50)
    info_textbox_register.pack(side=BOTTOM, pady=20)
    info_textbox_register.place(relx=0.4, rely=0.95)
    info_textbox_register.delete(0, "end")
    info_textbox_register.config(state=DISABLED)

    button_return_to_home_page = tk.Button(frame_register, text="home page", height=1, width=10, command=lambda:threaded_func(home_page, ("connect",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(side=LEFT, pady=10)
    button_return_to_home_page.place(x=100, y=50)

    first_text = tk.Label(frame_register,
                             text="first name:",
                             fg="black",
                             font="Verdana 25 bold underline"

                             )
    first_text.pack()
    first_text.place(relx=0.265, rely=0.2)

    global first_textbox
    first_textbox = Entry(frame_register, textvariable=first_register_var, width=27)
    first_textbox.pack(side=LEFT, padx=100)
    first_textbox.place(relx=0.28, rely=0.3)

    last_text = tk.Label(frame_register,
                             text="last name:",
                             fg="black",
                             font="Verdana 25 bold underline"
                             )
    last_text.pack(side=LEFT, padx=100)
    last_text.place(relx=0.27, rely=0.35)

    global last_textbox
    last_textbox = Entry(frame_register, textvariable=last_register_var, width=27)
    last_textbox.pack(side=LEFT, padx=100)
    last_textbox.place(relx=0.28, rely=0.45)

    gender_text = tk.Label(frame_register,
                         text="gender:",
                         fg="black",
                         font="Verdana 25 bold underline"
                         )
    gender_text.pack(side=LEFT, padx=100)
    gender_text.place(relx=0.29, rely=0.5)

    global radio_male
    radio_male = Radiobutton(frame_register, text="male", variable=gender_register_var, value="male", tristatevalue="default")
    radio_male.pack(anchor = tk.W)
    radio_male.place(relx=0.275, rely=0.6)

    global radio_female
    radio_female = Radiobutton(frame_register, text="female", variable=gender_register_var, value="female", tristatevalue="default")
    radio_female.pack(anchor = tk.W)
    radio_female.place(relx=0.375, rely=0.6)

    mikum_text = tk.Label(frame_register,
                           text="mikum:",
                           fg="black",
                           font="Verdana 25 bold underline"
                           )
    mikum_text.pack(side=LEFT, padx=100)
    mikum_text.place(relx=0.29, rely=0.65)

    global radio_center
    radio_center = Radiobutton(frame_register, text="center", variable=mikum_register_var, value="center",
                             tristatevalue="default")
    radio_center.pack(anchor=tk.W)
    radio_center.place(relx=0.4, rely=0.75)

    global radio_north
    radio_north = Radiobutton(frame_register, text="north", variable=mikum_register_var, value="north",
                               tristatevalue="default")
    radio_north.pack(anchor=tk.W)
    radio_north.place(relx=0.325, rely=0.75)

    global radio_south
    radio_south = Radiobutton(frame_register, text="south", variable=mikum_register_var, value="south",
                               tristatevalue="default")
    radio_south.pack(anchor=tk.W)
    radio_south.place(relx=0.25, rely=0.75)







    username_text = tk.Label(frame_register,
                    text="username:",
                    fg="black",
                    font="Verdana 25 bold underline"
                    )
    username_text.pack()
    username_text.place(relx=0.63, rely=0.2)

    global username_textbox
    username_textbox = Entry(frame_register, textvariable = name_register_var , width=27)
    username_textbox.pack()
    username_textbox.place(relx=0.645,rely=0.3)

    password_text = tk.Label(frame_register,
                    text="password:",
                    fg="black",
                    font="Verdana 25 bold underline"
                    )
    password_text.pack()
    password_text.place(relx=0.63, rely=0.35)

    global password_textbox
    password_textbox = Entry(frame_register,textvariable = passw_register_var ,show="*", width=27)
    password_textbox.pack()
    password_textbox.place(relx=0.645, rely=0.45)

    re_password_text = tk.Label(frame_register,
                             text="re-password:",
                             fg="black",
                             font="Verdana 25 bold underline"
                             )
    re_password_text.pack()
    re_password_text.place(relx=0.615, rely=0.5)

    global re_password_textbox
    re_password_textbox = Entry(frame_register, textvariable=re_passw_register_var, show="*", width=27)
    re_password_textbox.pack()
    re_password_textbox.place(relx=0.645, rely=0.6)

    email_text = tk.Label(frame_register,
                                text="email:",
                                fg="black",
                                font="Verdana 25 bold underline"
                                )
    email_text.pack()
    email_text.place(relx=0.66, rely=0.65)

    global email_textbox
    email_textbox = Entry(frame_register, textvariable=email_register_var, width=27)
    email_textbox.pack()
    email_textbox.place(relx=0.645, rely=0.75)



    """submit button"""

    submit_register_button = tk.Button(frame_register, text="register", height=1, width=7, command=lambda:threaded_func(register_submit, None))
    submit_register_button['font'] = myFont
    submit_register_button.pack(pady=10)
    submit_register_button.place(relx=0.445, rely=0.8)

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
    search_textbox.configure(font=("Verdana", 22))

    arr_of_filenames = get_user_filenames(This_Client.user.username)
    create_listbox("not destroy", arr_of_filenames)

    user_first_text = tk.Label(frame_request,
                               text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                               fg="black",
                               font="Verdana 25 bold underline"
                               )
    user_first_text.pack()
    user_first_text.place(relx=0.75, rely=0.2)

    files_text = tk.Label(frame_request,
                          text="files:",
                          fg="black",
                          font="Verdana 35 bold underline"
                          )
    files_text.pack()
    files_text.place(relx=0.46, rely=0.1)



    search_text = tk.Label(frame_request,
                          text="search:",
                          fg="black",
                          font="Verdana 25 bold underline"
                          )
    search_text.pack()
    search_text.place(relx=0.459, rely=0.175)

    search_button = tk.Button(frame_request, text="search", height=1, width=5, command=lambda:threaded_func(create_specific_listbox, None))
    search_button['font'] = myFont
    search_button.pack(pady=10)
    search_button.place(relx=0.4, rely=0.3)

    reset_button = tk.Button(frame_request, text="reset", height=1, width=5, command=lambda:threaded_func(create_listbox, ("destroy", arr_of_filenames)))
    reset_button['font'] = myFont
    reset_button.pack(pady=10)
    reset_button.place(relx=0.53, rely=0.3)

    get_file_button = tk.Button(frame_request, text="get file", height=1, width=7, command=lambda:threaded_func(call_net_request_file_and_open, (listbox_var,)))
    get_file_button['font'] = myFont
    get_file_button.pack(pady=10)
    get_file_button.place(relx=0.625, rely=0.8)

    delete_file_button = tk.Button(frame_request, text="delete file", height=1, width=7, command=lambda:threaded_func(delete_file, (listbox_var,)))
    delete_file_button['font'] = myFont
    delete_file_button.pack(pady=10)
    delete_file_button.place(relx=0.3, rely=0.8)

    save_file_button = tk.Button(frame_request, text="save file", height=1, width=7, command=lambda:threaded_func(call_net_request_file_and_save, (listbox_var,)))
    save_file_button['font'] = myFont
    save_file_button.pack(pady=10)
    save_file_button.place(relx=0.4625, rely=0.8)

    global directory_textbox
    directory_textbox = Entry(frame_request, width=28)
    directory_textbox.pack()
    directory_textbox.place(relx=0.4625, rely=0.75)
    directory_textbox.config(state=DISABLED)



    button_return_to_home_page = tk.Button(frame_request, text="disconnect", height=1, width=10,
                                           command=lambda:threaded_func(home_page, ("disconnected",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=100, y=50)

    request_image_button = tk.Button(frame_request, text="sending page", height=1, width=12, command=lambda:threaded_func(sending_page,None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=150)








def sending_page():
    global db_answer_textbox
    global path
    path = tk.StringVar()
    frame_default.destroy()
    frame_sending = create_frame()
    write(frame_sending, "sending page", 0.345)

    user_first_text = tk.Label(frame_sending,
                             text="Hello " + This_Client.user.first + " " + This_Client.user.last,
                             fg="black",
                             font="Verdana 25 bold underline"
                             )
    user_first_text.pack()
    user_first_text.place(relx=0.7, rely=0.3)

    file_sending_button = tk.Button(frame_sending, text="choose file", height=1, width=9, command=lambda:threaded_func(choose_file_to_send, None))
    file_sending_button['font'] = myFont
    file_sending_button.pack(pady=10)
    file_sending_button.place(relx=0.45, rely=0.4)

    global filename_textbox
    filename_textbox = Entry(frame_sending,textvariable=path , width=27)
    filename_textbox.pack()
    filename_textbox.place(relx=0.47, rely=0.6)


    button_send_image = tk.Button(frame_sending, text="send image", height=1, width=9,
                                  command=lambda:threaded_func(call_net_send_file, (This_Client.net, get_path(), False, "")))
    button_send_image['font'] = myFont
    button_send_image.pack()
    button_send_image.place(relx=0.45, rely=0.7)
    filename_textbox.config(state=DISABLED)

    button_return_to_home_page = tk.Button(frame_sending, text="disconnect", height=1, width=10, command=lambda:threaded_func(home_page, ("disconnected",)))
    button_return_to_home_page['font'] = myFont
    button_return_to_home_page.pack(pady=10)
    button_return_to_home_page.place(x=100, y=50)

    request_image_button = tk.Button(frame_sending, text="request page", height=1, width=12, command=lambda:threaded_func(request_page, None))
    request_image_button['font'] = myFont
    request_image_button.pack(pady=10)
    request_image_button.place(x=75, y=150)

    db_answer_textbox = Entry(frame_sending, width=40)
    db_answer_textbox.pack()
    db_answer_textbox.place(relx=0.44, rely=0.9)
    db_answer_textbox.config(state=DISABLED)




def write(frame, text, x):
    text = tk.Label(frame,
    text=text,
    fg="black",
    font="Verdana 50 bold underline"
    )
    text.pack(side=TOP, pady=50)
    text.place(relx=x)


net = network()
net.connect_to_server()
This_Client = client(net, None)


root = tk.Tk()
frame_default = tk.Frame()
frame_default.pack(fill='both', expand=True)
frame_default.bind('<Configure>', "1600x900")
write(frame_default, "UrCloud", 0.4)

myFont = font.Font(size=30)
button_login = tk.Button(frame_default, text="login", height=2, width=10, command=lambda:threaded_func(login, None))
button_login['font'] = myFont
button_login.pack()
button_login.place(relx=0.75, rely=0.6)


button_register = tk.Button(frame_default, text="register", height=2, width=10, command=lambda:threaded_func(register, None))
button_register['font'] = myFont
button_register.pack()
button_register.place(relx=0.1, rely=0.6)


root.geometry("1600x900+125+75")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()



