import socket
import os
import sqlite3
from PIL import Image
import pickle
import io
from PIL import ImageShow, Image
from array import array
from MyClasses import user, client, network, bool_and_string, file
import threading
import re
from Project_DBFunctions_pc import db_handler

alphabet = r"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRST1234567890 -+=:;_,.?!@#$%^&*()[]{}<>/"
key = "BrAiNdEaD"

letter_to_index = dict(zip(alphabet, range(len(alphabet))))
index_to_letter = dict(zip(range(len(alphabet)), alphabet))

def encrypt(message, key):
    encrypted = ""
    split_message = [
        message[i : i + len(key)] for i in range(0, len(message), len(key))
    ]

    for each_split in split_message:
        i = 0
        for letter in each_split:
            number = (letter_to_index[letter] + letter_to_index[key[i]]) % len(alphabet)
            encrypted += index_to_letter[number]
            i += 1

    return encrypted


def decrypt(cipher, key):
    decrypted = ""
    split_encrypted = [
        cipher[i : i + len(key)] for i in range(0, len(cipher), len(key))
    ]

    for each_split in split_encrypted:
        i = 0
        for letter in each_split:
            number = (letter_to_index[letter] - letter_to_index[key[i]]) % len(alphabet)
            decrypted += index_to_letter[number]
            i += 1

    return decrypted

def get_secondary_filename(arr, filename):

    f = True
    index = 0
    for i in range(1, len(arr) + 1):
        filename2 = filename + "(" + str(i) + ")"
        for filename_arr in arr:
            if(filename_arr == filename2):
                f = False
        if(f == True):
            return filename2
        f = True
        index = i

    filename2 = filename + "(" + str(index + 1) + ")"
    return filename2

def get_specific_filename_arr(filename_arr, filename):
    arr = []
    re_check_str = "^" + filename + "[(][0-9]+[)]$"
    for arr_filename in filename_arr:
        check = re.findall(re_check_str, arr_filename)
        if(check != []):
            arr.append(arr_filename)
    return arr

def fix_filename(filename):
    re_check_str = "^.+[(][0-9]+[)]$"
    check = re.findall(re_check_str, filename)
    if(check != []):
        arr = filename.split("(")
        arr.pop()
        fixed_filename = "(".join(arr)
        return fixed_filename
    return filename


db_server_net = network()
db_socket = db_server_net.net_socket
db_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
db_socket.bind(('127.0.0.1', 3969))
db_socket.listen(10)

users_db_handler = db_handler("users")
files_db_handeler = db_handler("files")
groups_db_handler = db_handler("groups")

print("db is running")

server_socket, server_port = db_socket.accept()
global flag
flag = "default"
while (True):
    try:
        flag = server_socket.recv(50).decode()
        server_socket.send("got flag".encode())
        print(flag)
    except Exception as ex:
        print(ex)
        client_socket, client_port = server_socket.accept()

    try:
        if (flag == "override file"):
            size = int(str(server_socket.recv(4069).decode()))
            server_socket.send("got size".encode())

            file_bytes = b""
            file_bytes += server_socket.recv(size)

            file_object = server_socket.recv(500)
            file_object = pickle.loads(file_object)

            username = server_socket.recv(4069).decode()

            files_db_handeler.delete_file_by_filename(file_object.file, username, file_object.group)
            files_db_handeler.insert_file(file_object, file_bytes)

        if(flag == "kick member"):
            member_and_group = server_socket.recv(40).decode()
            member = member_and_group.split(",")[0]
            group = member_and_group.split(",")[1]
            answer = groups_db_handler.kick_user_from_group(group, member, files_db_handeler)
            server_socket.send(answer.encode())

        if (flag == "check username"):
            username = server_socket.recv(4069).decode()

            answer = users_db_handler.check_if_username_exist(username)

            server_socket.send(answer.encode())

        if (flag == "create group"):
            group_object = server_socket.recv(1000)
            group_obj = pickle.loads(group_object)
            db_answer = groups_db_handler.create_new_group(group_obj.host, group_obj.group_name, group_obj.password)

            server_socket.send(db_answer.encode())

        if (flag == "get users groups"):
            username = server_socket.recv(20).decode()

            users_groups_arr = groups_db_handler.get_users_groups(username)
            arr_bytes = pickle.dumps(users_groups_arr, 0)
            server_socket.sendall(arr_bytes)

        if (flag == "join group"):
            request_object = server_socket.recv(1000)
            request_object = pickle.loads(request_object)
            db_answer = groups_db_handler.add_user_to_group(request_object.group_name, request_object.username, request_object.password)
            print(db_answer)

            server_socket.send(db_answer.encode())


        if (flag == "check email"):
            email = server_socket.recv(4069).decode()
            answer = users_db_handler.check_if_email_exist(email)

            server_socket.send(answer.encode())


        if (flag == "delete file"):
            delete_object = pickle.loads(server_socket.recv(4069))
            rcv_username = delete_object.username
            rcv_filename = delete_object.filename
            rcv_group = delete_object.group

            fake_arr = rcv_filename.split(".")
            fake_arr.pop()
            rcv_filename = ".".join(fake_arr)

            files_db_handeler.delete_file_by_filename(rcv_filename, rcv_username, rcv_group)


        if (flag == "sending file"):
            size = int(str(server_socket.recv(4069).decode()))
            server_socket.send("got size".encode())

            rcv_file = b""
            rcv_file += server_socket.recv(size)

            file_object = server_socket.recv(4069)
            file_object = pickle.loads(file_object)
            print(file_object.file + "," + file_object.group)

            check_answer = files_db_handeler.check_if_file_exist(file_object.user, file_object.file, file_object.type, file_object.group)
            print(check_answer)
            if(check_answer != None):
                files_db_handeler.insert_file(file_object, rcv_file)
                server_socket.send("your file uploaded successfuly".encode())

            else:
                fixed_filename = fix_filename(file_object.file)
                check_answer2 = files_db_handeler.check_if_file_exist(file_object.user, fixed_filename, file_object.type, file_object.group)
                if(check_answer2 != None):
                    server_socket.send(fixed_filename.encode())

                    """file_object.filename = fixed_filename
                    files_db_handeler.insert_file(file_object, rcv_file)"""


                else:
                    filename_arr = files_db_handeler.get_all_filenames_of_user(file_object.user, file_object.group)
                    specific_filename_arr = get_specific_filename_arr(filename_arr, fixed_filename)
                    fixed_filename = get_secondary_filename(specific_filename_arr, fixed_filename)
                    server_socket.send(fixed_filename.encode())


            """file_data = files_db_handeler.search_file("guybar", "image3")[1]
            file_data = file_data[2:-2:]
            print(file_data)
            file_bytes = bytes(file_data)

            file_arr = io.BytesIO(file_bytes)
            opened_file = Image.open(file_arr)
            opened_file.show()"""

            """
            l = len(file_object.file.split("/")) - 1
            img_name = file_object.file.split("/")[l]"""

            #folder_path = r"C:\Users\liorp\PycharmProjects\project\db_files"
            """file_path = os.path.join(folder_path, img_name)
            opened_file.save(file_path, file_object.type)"""

        if(flag == "request file"):
            request_data = str(server_socket.recv(4069).decode())
            username = request_data.split(",")[0]
            filename = request_data.split(",")[1]
            group_name = request_data.split(",")[2]
            print(username)
            print(filename)
            print(group_name)
            answer = files_db_handeler.search_file(username, filename, group_name)
            if(answer != None):
                requested_file_object = file(answer[0], answer[2], answer[3], answer[4], answer[5])
                requested_file_bytes = answer[1]
                server_socket.send("found image".encode())
                server_socket.send(pickle.dumps(requested_file_object, 0))
                server_socket.sendall(requested_file_bytes)
            else:
                server_socket.send("no image found".encode())

        if (flag == "get group members"):
            group_name = server_socket.recv(20).decode()
            print(group_name)
            users_arr = groups_db_handler.get_group_members(group_name)
            print(users_arr)
            arr_bytes = pickle.dumps(users_arr, 0)
            server_socket.sendall(arr_bytes)

        if (flag == "sending register data"):
            register_data = str(server_socket.recv(4069).decode())
            users_db_handler.insert_user(register_data)

        if(flag == "close group"):
            group_name = server_socket.recv(30).decode()
            groups_db_handler.close_group(group_name, files_db_handeler)

        if (flag == "get groups files"):
            group_name = server_socket.recv(40).decode()

            arr_of_group_files = files_db_handeler.get_all_files_of_group(group_name)
            print(arr_of_group_files)
            arr_bytes = pickle.dumps(arr_of_group_files, 0)
            server_socket.sendall(arr_bytes)

        if (flag == "sending login data"):
            login_data = str(server_socket.recv(4069).decode())
            answer = users_db_handler.search_user(login_data)
            server_socket.send(answer.encode())

        if (flag == "get user filename arr"):
            username = server_socket.recv(4069).decode()
            arr = files_db_handeler.get_all_filenames_of_user2(username)
            server_socket.send(pickle.dumps(arr, 0))

    except Exception as ex:
        print(ex)
        server_socket, server_port = db_socket.accept()


