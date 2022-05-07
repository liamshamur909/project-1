import socket
import pickle
import os

class client():
    def __init__(self, net, user):
        self.net = net
        self.user = user

class username_filename_and_group():
    def __init__(self, username, filename, group):
        self.username = username
        self.filename = filename
        self.group = group

class user():
    def __init__(self, first, last, gender, mikum, username, password, re_passwowrd, email):
        self.first = first
        self.last = last
        self.gender = gender
        self.mikum = mikum
        self.username = username
        self.password = password
        self.re_password = re_passwowrd
        self.email = email

class network:
    def __init__(self):
        self.net_socket = socket.socket()

    def connect_to_server(self):
        self.net_socket.connect(("127.0.0.1", 3960))

    def connect_to_db(self):
        self.net_socket.connect(("127.0.0.1", 3969))

    def send_file(self, file, size):
        self.net_socket.sendall(str(size).encode())
        answer = self.net_socket.recv(20).decode()

        if (answer == "got size"):
            self.net_socket.sendall(file)

    def send_file_object(self, file):
        self.net_socket.sendall(pickle.dumps(file, 0))

    def send_flag(self, flag):
        self.net_socket.send(flag.encode())

    def send_register(self, first, last, gender, mikum, username, password, re_password, email):
        register_string = first + "," + last + "," + gender + "," + mikum + "," + username + "," + password + "," + re_password + "," + email
        self.net_socket.send(register_string.encode())

    def send_login(self, username, password):
        login_string = username + "," + password
        self.net_socket.send(login_string.encode())

    def send_request_file_data(self, username, filename, group_name):
        request_string = username + "," + filename + "," + group_name
        self.net_socket.send(request_string.encode())

    def send_group_object(self, group):
        self.net_socket.sendall(pickle.dumps(group, 0))

    def send_request_object(self, request):
        self.net_socket.sendall(pickle.dumps(request, 0))

class file:
    def __init__(self, user, file, type, size, group):
        self.user = user
        self.file = file
        self.type = type
        self.size = size
        self.group = group

class group_object:
    def __init__(self, host, group_name, password, members):
        self.host = host
        self.group_name = group_name
        self.password = password
        self.member = members

class client_join_request:
    def __init__(self, username, group_name, password):
        self.username = username
        self.group_name = group_name
        self.password = password

class bool_and_string:
    def __init__(self, flag, text):
        self.flag = flag
        self.text = text
    def GetFlag(self):
        return self.flag
    def GetText(self):
        return self.text


