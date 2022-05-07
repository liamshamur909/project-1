import socket
import pickle
import io
from PIL import ImageFile, Image
from array import array
from MyClasses import user, client, network, bool_and_string
import threading
import time

ImageFile.LOAD_TRUNCATED_IMAGES = True

def threaded_main(client_socket, thread_num):
    global flag
    flag = "default"
    while (True):
        try:
            flag = client_socket.recv(50).decode()
            client_socket.send("got flag".encode())
            print(flag)

        except Exception as ex:
            print(ex)
            client_socket, client_port = server_socket.accept()

        try:
            if (flag == "override file"):
                size = int(str(client_socket.recv(30).decode()))
                print(size)
                client_socket.sendall("got size".encode())
                file_bytes = b""
                file_bytes += client_socket.recv(size)
                file_object = client_socket.recv(1000)
                username = client_socket.recv(4069).decode()
                server_db_net.send_flag("override file")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.send_file(file_bytes, size)
                    server_db_net.net_socket.send(file_object)
                    server_db_net.net_socket.send(username.encode())

            if (flag == "delete file"):
                delete_object = pickle.loads(client_socket.recv(4069))

                server_db_net.send_flag("delete file")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(pickle.dumps(delete_object, 0))

            if(flag == "close group"):
                group_name = client_socket.recv(30)
                server_db_net.send_flag("close group")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(group_name)

            if(flag == "create group"):
                group_object = pickle.loads(client_socket.recv(1000))

                server_db_net.send_flag("create group")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.send_group_object(group_object)

                db_answer = server_db_net.net_socket.recv(30).decode()
                client_socket.send(db_answer.encode())

            if(flag == "kick member"):
                member_and_group = client_socket.recv(40)

                server_db_net.send_flag("kick member")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(member_and_group)

                db_answer = server_db_net.net_socket.recv(30).decode()
                client_socket.send(db_answer.encode())

            if(flag == "get groups files"):
                group_name = client_socket.recv(40)

                server_db_net.send_flag("get groups files")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(group_name)

                    files_arr = server_db_net.net_socket.recv(4069)
                    print(pickle.loads(files_arr))
                    client_socket.sendall(files_arr)

            if (flag == "join group"):
                request_object = pickle.loads(client_socket.recv(1000))

                server_db_net.send_flag("join group")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.send_request_object(request_object)

                db_answer = server_db_net.net_socket.recv(100).decode()
                print(db_answer)
                client_socket.send(db_answer.encode())

            if (flag == "get users groups"):
                username = client_socket.recv(20)
                server_db_net.send_flag("get users groups")

                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(username)

                    groups_arr = server_db_net.net_socket.recv(4069)
                    groups_arr = pickle.loads(groups_arr)
                    client_socket.sendall(pickle.dumps(groups_arr), 0)

            if (flag == "get group members"):
                group_name = client_socket.recv(20)
                server_db_net.send_flag("get group members")

                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(group_name)

                    users_arr = server_db_net.net_socket.recv(4069)
                    users_arr = pickle.loads(users_arr)
                    client_socket.sendall(pickle.dumps(users_arr), 0)

            if (flag =="check username"):
                username = client_socket.recv(4069).decode()

                server_db_net.send_flag("check username")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(username.encode())

                    answer = db_socket.recv(4069).decode()
                    client_socket.send(answer.encode())

            if (flag =="check email"):
                email = client_socket.recv(4069).decode()

                server_db_net.send_flag("check email")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.net_socket.send(email.encode())

                    answer = db_socket.recv(4069).decode()
                    client_socket.send(answer.encode())


            if (flag == "sending file"):
                size = int(str(client_socket.recv(4069).decode()))
                client_socket.send("got size".encode())

                file_bytes = b""
                file_bytes += client_socket.recv(size)

                file_object = client_socket.recv(4069)
                file_object = pickle.loads(file_object)

                server_db_net.send_flag("sending file")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    server_db_net.send_file(file_bytes, size)
                    server_db_net.send_file_object(file_object)

                    db_answer = db_socket.recv(4069).decode()
                    client_socket.send(db_answer.encode())

            if(flag == "request file"):
                request_data = str(client_socket.recv(4069).decode())
                server_db_net.send_flag("request file")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    db_socket.send(request_data.encode())
                    mini_flag = str(db_socket.recv(4069).decode())
                    if(mini_flag == "found image"):
                        rcv_object = db_socket.recv(4069)
                        requested_file_object = pickle.loads(rcv_object)

                        requested_file_bytes = b""
                        print(requested_file_object.size)
                        requested_file_bytes += db_socket.recv(int(requested_file_object.size))

                        """file_arr = io.BytesIO(requested_file_bytes)
                        opened_file = Image.open(file_arr)
                        opened_file.show()"""

                        client_socket.send("found image".encode())
                        client_socket.send(pickle.dumps(requested_file_object, 0))
                        client_socket.sendall(requested_file_bytes)

                    else:
                        client_socket.send("no image found".encode())


            if (flag == "sending register data"):
                register_data = str(client_socket.recv(4069).decode())
                server_db_net.send_flag("sending register data")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    db_socket.send(register_data.encode())

            if (flag == "sending login data"):
                login_data = client_socket.recv(4069).decode()
                server_db_net.send_flag("sending login data")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    db_socket.send(login_data.encode())
                    db_response = db_socket.recv(4069).decode()
                    username = db_response.split(",")[5]
                    f = False
                    if(username_list != []):
                        for value in username_list:
                            if(value == username):
                                client_socket.send("the user is already connected".encode())
                                f = True
                    if(f == False):
                        if(db_response.split(",")[0] == "True"):
                            username_list.append(username)
                        client_socket.send(db_response.encode())

                print(username_list)

            if (flag == "get user filename arr"):
                username = client_socket.recv(4069).decode()
                server_db_net.send_flag("get user filename arr")
                answer = server_db_net.net_socket.recv(15).decode()
                if (answer == "got flag"):
                    db_socket.send(username.encode())

                    arr = db_socket.recv(4069)
                    arr = pickle.loads(arr)
                    client_socket.send(pickle.dumps(arr, 0))

            if (flag == "disconnect user"):
                username = client_socket.recv(4069).decode()
                username_list.remove(username)
                print(username_list)

        except Exception as ex:
            print(ex)
            client_socket, client_port = server_socket.accept()


server_client_net = network()
server_socket = server_client_net.net_socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 3960))

server_db_net = network()
server_db_net.connect_to_db()
db_socket = server_db_net.net_socket





thread_list = []
username_list = []
print("server running")

server_socket.listen(25)
i = 0
while(True):
    client_socket, client_port = server_socket.accept()
    client_handler = threading.Thread(target=threaded_main, args=(client_socket, i))
    client_handler.start()
    thread_list.append(client_handler)
    i = i + 1






