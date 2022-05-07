import sqlite3
import re
import pickle
from PIL import Image
import io
from MyClasses import file

class db_handler:
    def __init__(self, str_conn):
        self.table_name = str_conn
        self.conn = sqlite3.connect(str_conn + ".db")
        self.c = self.conn.cursor()

    def insert_user(self, user):
        user_data = user.split(",")
        self.c.execute(("""INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""), (encrypt(user_data[0], key), encrypt(user_data[1], key),
                                                                                   encrypt(user_data[2], key), encrypt(user_data[3], key), encrypt(user_data[4], key),
                                                                                   encrypt(user_data[5], key), encrypt(user_data[6], key), encrypt(user_data[7], key)))
        self.conn.commit()

    def search_user(self, user):
        user_data = user.split(",")
        self.c.execute(("""SELECT * FROM users WHERE user=(?) and password=(?)"""), (encrypt(user_data[0], key), encrypt(user_data[1], key)))
        db_answer = self.c.fetchone()

        if db_answer != None:
            answer = []
            for a in db_answer:
                answer.append(decrypt(a, key))
            return "True" + "," + ",".join(answer)
        return "False, "

    def show_all_users(self):
        self.c.execute("""SELECT * FROM users""")
        answer = self.c.fetchall()
        for user in answer:
            print(user)

    def show_all_files(self):
        self.c.execute("""SELECT * FROM files""")
        answer = self.c.fetchall()
        for file in answer:
            print(file)

    def delete_user_by_username(self, username):
        self.c.execute(("""DELETE FROM users WHERE user=(?)"""), (encrypt(username, key),))
        self.conn.commit()

    def delete_file_by_user(self, user):
        self.c.execute(("""DELETE FROM files WHERE user=(?)"""), (encrypt(user, key),))
        self.conn.commit()

    def delete_file_by_filename(self, filename, username, group_name):
        self.c.execute(("""DELETE FROM files WHERE filename=(?) and user=(?) and group_name=(?)"""), (encrypt(filename, key), encrypt(username, key), encrypt(group_name, key)))
        self.conn.commit()

    def insert_file(self, file_object, file):
        self.c.execute(("""INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)"""),(encrypt(file_object.user, key), file, encrypt(file_object.file, key), encrypt(file_object.type, key), file_object.size, encrypt(file_object.group, key)))
        self.conn.commit()

    def search_file(self, user, filename, group_name):
        self.c.execute("""SELECT * FROM files WHERE user=(?) and filename=(?) and group_name=(?)""", (encrypt(user, key), encrypt(filename, key), encrypt(group_name, key)))
        answer = self.c.fetchone()
        if answer != None:
            answer = (decrypt(answer[0], key), answer[1], decrypt(answer[2], key), decrypt(answer[3], key),answer[4], decrypt(answer[5], key))
            return answer
        return None

    def get_all_filenames_of_user(self, user, group_name):
        arr = []
        self.c.execute("""SELECT filename FROM files WHERE user=(?) and group_name=(?)""", (encrypt(user, key), encrypt(group_name, key)))
        answer = self.c.fetchall()
        print(answer)
        for filename in answer:
            arr.append(decrypt(filename[0], key))
        return arr

    def delete_all_group_files(self, group_name):
        self.c.execute(("""DELETE FROM files WHERE group_name=(?)"""), (encrypt(group_name, key),))
        self.conn.commit()

    def get_all_files_of_group(self, group):
        self.c.execute("""SELECT * FROM files WHERE group_name=(?)""", (encrypt(group, key),))
        answer = self.c.fetchall()
        arr = []
        for f in answer:
            arr.append(decrypt(f[2], key) + "." + decrypt(f[3], key))
            arr.append(decrypt(f[0], key))
        return arr

    def get_all_filenames_of_user2(self, user):
        arr = []
        self.c.execute("""SELECT filename FROM files WHERE user=(?) and group_name=(?)""", (encrypt(user, key), encrypt("Null", key)))
        answer1 = self.c.fetchall()

        self.c.execute("""SELECT type FROM files WHERE user=(?) and group_name=(?)""", (encrypt(user, key), encrypt("Null", key)))
        answer2 = self.c.fetchall()

        index = 0
        while(index < len(answer1)):
            arr.append(decrypt(answer1[index][0], key) + "." + decrypt(answer2[index][0], key))
            index = index + 1

        return arr

    def check_if_file_exist(self, user, filename, type, group_name):
        if(group_name == "Null"):
            self.c.execute("""SELECT * FROM files WHERE user=(?) and filename=(?) and type=(?)""",(encrypt(user, key), encrypt(filename, key), encrypt(type, key)))
            answer = self.c.fetchall()
            if (answer == []):
                return filename
            else:
                return None

        self.c.execute("""SELECT * FROM files WHERE user=(?) and filename=(?) and type=(?) and group_name=(?)""", (encrypt(user, key), encrypt(filename, key), encrypt(type, key), encrypt(group_name, key)))
        answer = self.c.fetchall()
        print(answer)
        if(answer == []):
            return filename
        return None

        #filename = fix_filename(filename)
        #self.c.execute("""SELECT * FROM files WHERE user=(?), filename=(?) and type=(?)""", (user, filename, type))
        #answer = self.c.fetchall()
        #if(answer == None):
        #    return filename

    def check_if_username_exist(self, username):
        self.c.execute("""SELECT * FROM users WHERE user=(?)""", (encrypt(username, key),))
        answer = self.c.fetchall()
        if(answer == []):
            return "False"
        return "True"

    def check_if_email_exist(self, email):
        self.c.execute("""SELECT * FROM users WHERE email=(?)""", (encrypt(email, key),))
        answer = self.c.fetchall()
        if(answer == []):
            return "False"
        return "True"

    def check_if_group_name_exist(self, group_name):
        self.c.execute(("""SELECT * FROM groups WHERE group_name=(?)"""), (encrypt(group_name, key),))
        answer = self.c.fetchall()
        if(answer != []):
            return True
        return False

    def create_new_group(self, host, group_name, passw):
        if(self.check_if_group_name_exist(group_name) == True):
            return "the group is already exist"
        else:
            arr = []
            arr.append(encrypt(host, key))
            self.c.execute(("""INSERT INTO groups VALUES (? ,?, ?, ?)"""), (encrypt(group_name, key), pickle.dumps(arr), encrypt(host, key), encrypt(passw, key)))
            self.conn.commit()
            return "the group created"

    def show_all_groups(self):
        self.c.execute("""SELECT * FROM groups""")
        answer = self.c.fetchall()
        for file in answer:
            print(file)

    def give_all_groups(self):
        self.c.execute("""SELECT * FROM groups""")
        answer = self.c.fetchall()
        return answer

    def get_group_members(self, group_name):
        try:
            self.c.execute(("""SELECT members FROM groups WHERE group_name=(?)"""), (encrypt(group_name, key),))
            bytes_arr = self.c.fetchall()
            arr = pickle.loads(bytes_arr[0][0])
            print(arr)
            i = 0
            for member in arr:
                arr[i] = decrypt(member, key)
                i = i + 1

            return arr
        except:
            return "the group doesnt exist"

    def get_group_by_group_name(self, group_name):
        try:
            self.c.execute(("""SELECT * FROM groups WHERE group_name=(?)"""), (encrypt(group_name, key),))
            arr = self.c.fetchall()
            arr = arr[0]
            arr = (decrypt(arr[0], key), arr[1], decrypt(arr[2], key), decrypt(arr[3], key))
            return arr
        except:
            return "the group doesnt exist"

    def add_user_to_group(self, group_name, username, password):
        try:
            group_data = self.get_group_by_group_name(group_name)
            arr = self.get_group_members(group_name)
            print(group_data)
            print(arr)
            if(group_data[3] != password):
                return "either the group name or password are incorrect"
            for user in arr:
                if(user == username):
                    return "the user is already in the group"
            arr.append(username)
            i = 0
            for member in arr:
                arr[i] = encrypt(member, key)
                i = i + 1
            bytes_arr = pickle.dumps(arr)
            self.c.execute(("""UPDATE groups SET members=(?) WHERE group_name=(?)"""), (bytes_arr, encrypt(group_name, key)))
            self.conn.commit()
            return "the user joined the group"
        except:
            return "either the group name or password are incorrect"

    def kick_user_from_group(self, group_name, username, files_db_handeler):
        arr = self.get_group_members(group_name)
        if(arr[0] == username):
            self.close_group(group_name, files_db_handeler)
            return "the group closed"

        arr2 = arr
        for user in arr:
            if(user == username):
                arr2.remove(username)
                i = 0
                for member in arr2:
                    arr2[i] = encrypt(member, key)
                    i = i + 1
                bytes_arr = pickle.dumps(arr2)
                self.c.execute(("""UPDATE groups SET members=(?) WHERE group_name=(?)"""), (bytes_arr, encrypt(group_name, key)))
                self.conn.commit()
                return "the user was removed"
        return "the user wasnt a member at all"

    def get_users_groups(self, username):
        users_groups_arr = []
        groups_arr = self.give_all_groups()
        print(groups_arr)
        for group in groups_arr:
            print(group)
            members_arr = self.get_group_members(decrypt(group[0], key))
            print(members_arr)
            for member in members_arr:
                print(member)
                if(member == username):
                    users_groups_arr.append(decrypt(group[0],key))
        print(users_groups_arr)
        return users_groups_arr


    def close_group(self, group_name, files_db_handeler):
        self.c.execute(("""DELETE FROM groups WHERE group_name=(?)"""), (encrypt(group_name, key),))
        files_db_handeler.delete_all_group_files(group_name)
        self.conn.commit()



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


def create_user_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE users(
                first text,
                last text,
                gender text,
                mikum text,
                user text,
                password text,
                re_password text,
                email text)""")

def create_files_table():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE files(
                user text,
                file BLOB,
                filename text,
                type text,
                size text,
                group_name text)""")

def create_groups_table():
    conn = sqlite3.connect("groups.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE groups(
                group_name text,
                members BLOB,
                host text,
                password text)""")

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

#files_db_handler = db_handler("files")
#users_db_handler = db_handler("users")
#groups_db_handler = db_handler("groups")

#host = "liam909"
#group_name = "ther_noobars"
#print(groups_db_handler.create_new_group(host, group_name, "123456"))

#print(groups_db_handler.give_all_groups())
#groups_db_handler.close_group("test_group1", "liam909")
#print(groups_db_handler.add_user_to_group("ther_noobars", "TheNoobOne", "123456"))
#print(groups_db_handler.get_group_members("ther_noobars"))
#print(groups_db_handler.get_group_members("the braindeads"))
#print(groups_db_handler.kick_user_from_group("the_braindeads", "doron"))
#print(groups_db_handler.get_group_by_group_name("the_braindeads"))
#groups_db_handler.show_all_groups()
#print(groups_db_handler.get_users_groups("doron1408"))
#users_db_handler.insert_user("user_data")1
#print(users_db_handler.search_user("guybar69,guybar96"))

#users_db_handler.delete_user_by_username("assafmende")
#users_db_handler.show_all_users()

#files_db_handler.insert_file(file("liam909", "image1.png", "png", "4546"), "baranes")
#files_db_handler.delete_file_by_filename("image4", "liam909", "test_group1")

#print(files_db_handler.search_file("guybar", "image3"))
#print(files_db_handler.check_if_file_exist("liam909", "image11", "png"))
#files_db_handler.show_all_files()

#files_db_handler.conn.commit()
#files_db_handler.conn.close()

#users_db_handler.conn.commit()
#users_db_handler.conn.close()

#groups_db_handler.conn.commit()
#groups_db_handler.conn.close()

