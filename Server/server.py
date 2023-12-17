import socket
import threading
import json
import group_manager
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


class Server(group_manager.GroupManager):

    def __init__(self):
        db_password = os.getenv("DB_PASSWORD")
        ip_address = os.getenv("IP_ADDRESS")
        std_port = os.getenv("STD_PORT")
        max_clients = os.getenv("MAX_CLIENTS")

        if ip_address is None:
            ip_address = input("Enter your ip address: ")
        if std_port is None:
            std_port = input("Enter the port for your server: ")
        if db_password is None:
            db_password = input("Enter your db password to connect to the database: ")
        if max_clients is None:
            max_clients = input("Specify how many clients can connect at the same time: ")

        super().__init__(db_password)

        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                port=3308,
                user="root",
                passwd=f"{db_password}"
            )
        except mysql.connector.errors:
            print("Cant connect to database. Make sure your database is running and you use the correct password.")

        self.mycursor = self.mydb.cursor(buffered=True)
        self.mycursor.execute("CREATE DATABASE IF NOT EXISTS consolechat")
        self.mycursor.execute("USE consolechat")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS Users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), ip VARCHAR(255), port INT(255))")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS ChatHistory (id INT AUTO_INCREMENT PRIMARY KEY, receiver_id INT, sender_id INT, message VARCHAR(512))")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS GroupChats (group_id INT AUTO_INCREMENT PRIMARY KEY, group_name VARCHAR(255), admin_id INT)")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS GroupMembers (id INT AUTO_INCREMENT PRIMARY KEY, group_id INT, user_id INT)")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS GroupChatHistory (id INT AUTO_INCREMENT PRIMARY KEY, group_id INT, sender_id INT, message VARCHAR(512))")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server_address = (str(ip_address), int(std_port))
            self.server_socket.bind(self.server_address)
            self.server_socket.listen(int(max_clients))
        except OSError:
            print("Error while trying to start server. Make sure your ip address and port is correct.")
            quit()
        except ValueError:
            print("Error while trying to start server. Make sure your ip address and port is correct.")
            quit()

        self.clients = {}
        self.client_id = {}

    def start_server(self):
        while True:
            client_socket, client_adress = self.server_socket.accept()
            print(f"Connection established from {client_adress}")

            handle_process = threading.Thread(target=self.handle_client, args=(client_socket, client_adress))
            handle_process.start()

    def handle_client(self, client_socket, client_adress):
        client_login = False

        while True:
            msg = client_socket.recv(1024)
            print(msg)

            print(f"Received message from {client_adress}: {msg.decode('utf-8')}")

            received_data = msg.decode('utf-8')
            if received_data.startswith("!signin"):
                signin_credentials = client_socket.recv(1024)
                if self.check_client_is_online(client_socket, signin_credentials):
                    signin_credentials = signin_credentials.decode("utf-8")
                    json_data = json.loads(signin_credentials)
                    print(json_data)
                    if self.check_login_credentials(json_data["username"], json_data["password"]):
                        try:
                            client_socket.send(bytes("!successful", "utf8"))
                        except BrokenPipeError:
                            print("Cannot send answer")

                        self.handle_client_login(client_socket, json_data)
                        client_login = True
                    else:
                        try:
                            client_socket.send(bytes("!login failed", "utf8"))
                        except BrokenPipeError:
                            print("Cannot send answer")
                else:
                    break

            if received_data.startswith("!register"):
                check_register_credentials = client_socket.recv(1024)
                if self.check_client_is_online(client_socket, check_register_credentials):
                    json_data = json.loads(check_register_credentials)
                    print(json_data)
                    if self.is_user_registered(json_data["username"]):
                        print("function is user registered reached")
                        try:
                            client_socket.send(bytes("!already taken", "utf8"))
                        except BrokenPipeError:
                            print("cannot send answer")
                    else:
                        self.register_in_db(json_data, client_adress)
                        try:
                            client_socket.send(bytes("!successful", "utf8"))
                        except BrokenPipeError:
                            print("Cannot send answer")

                        self.handle_client_login(client_socket, json_data)
                        client_login = True
                else:
                    break

            print(received_data)
            if received_data.startswith("!chat") and client_login:
                message_partner = client_socket.recv(1024)
                if self.check_client_is_online(client_socket, message_partner):
                    if self.is_user_registered(message_partner):
                        try:
                            client_socket.send(bytes("!user exists", "utf8"))
                        except BrokenPipeError:
                            print("Cannot send answer")
                        chat_members = client_socket.recv(1024)

                        if self.check_client_is_online(client_socket, chat_members):

                            chat_members = chat_members.decode("utf-8")
                            chat_members_parts = chat_members.split("|")

                            target_username = chat_members_parts[0]
                            print(target_username)
                            username = chat_members_parts[1]
                            ids = self.get_chat_member_ids(target_username, username)
                            target_id = ids[0]
                            client_id = ids[1]
                            try:
                                client_socket.send(bytes(f"{target_id}|{client_id}", "utf8"))

                            except BrokenPipeError:
                                print("Cannot send answer")
                        else:
                            break
                    else:
                        try:
                            client_socket.send(bytes("!user doesnt exist", "utf8"))
                        except BrokenPipeError:
                            print("Cannot send answer")
                        continue
                else:
                    break

                target_id = client_socket.recv(256)
                target_id = str(target_id.decode("utf-8")).strip("(), ")
                print("target id:", target_id)
                chat_history = self.get_chat_history(self.client_id[client_socket], target_id)
                try:
                    client_socket.send(bytes(str(chat_history), "utf8"))
                except BrokenPipeError:
                    print("Cannot send chat history")

                while True:
                    msg = client_socket.recv(512)
                    msg = msg.decode("utf-8")
                    parts = msg.split("|")
                    if msg == "!exit":
                        break
                    if self.check_client_is_online(client_socket, msg):
                        if len(parts) != 3:
                            client_socket.close()
                        receiver_id = int(parts[0].strip("(), "))
                        client_id = int(parts[1].strip("(), "))
                        message = parts[2]
                        self.insert_chat_message(receiver_id, client_id, message)

                continue

            if received_data.startswith("!create_group") and client_login:
                group_information = client_socket.recv(512)
                group_information = group_information.decode("utf8")
                try:
                    parts = group_information.split("|")
                    group_name = parts[0]
                    admin_id = parts[1]
                    group_admin_id = self.get_user_id(admin_id)
                    group_id = self.get_existing_group_id_by_name(group_name)

                    if group_admin_id:
                        if group_manager.GroupManager.create_group(self, group_name, group_admin_id):
                            client_socket.send(bytes("Group was created", "utf8"))
                        else:
                            client_socket.send(bytes(f"A group with the name {group_name} already exists", "utf8"))

                except (IndexError, UnicodeDecodeError):
                    client_socket.send(bytes("An error occurred while creating a group", "utf8"))

            if received_data.startswith("!add_user_to_group") and client_login:
                user_to_add_group_data = client_socket.recv(512)
                user_to_add_group_data = user_to_add_group_data.decode("utf8")
                try:
                    parts = user_to_add_group_data.split("|")
                    user_to_add = parts[0]
                    group_to_add = parts[1]
                    client_id = parts[2]
                    group_id = self.get_existing_group_id_by_name(group_to_add)
                    admin_id = group_manager.GroupManager.get_group_admin(self, group_id)
                    user_id_to_add = self.get_user_id(user_to_add)

                    print(admin_id)
                    print(client_id)

                    if admin_id != client_id:
                        client_socket.send(bytes(f"You are not the owner of the group {group_to_add}", "utf8"))
                    elif not user_id_to_add:
                        client_socket.send(bytes("This user does not exist", "utf8"))
                    elif not group_id:
                        client_socket.send(bytes("This group does not exist", "utf8"))
                    else:
                        if group_manager.GroupManager.add_user_to_group(self, group_id, user_id_to_add):
                            client_socket.send(bytes(f"User was successfully added to {group_to_add}", "utf8"))
                        else:
                            client_socket.send(bytes(f"User {user_to_add} was already in your group", "utf8"))

                except (IndexError, UnicodeDecodeError):
                    client_socket.send(bytes("An error occurred while adding the user to the group", "utf8"))

            if received_data.startswith("!remove_user_from_group") and client_login:
                user_to_remove_group_data = client_socket.recv(512)
                user_to_remove_group_data = user_to_remove_group_data.decode("utf8")
                try:
                    parts = user_to_remove_group_data.split("|")
                    user_to_remove = parts[0]
                    group_to_remove = parts[1]
                    client_id = parts[2]
                    group_id = self.get_existing_group_id_by_name(group_to_remove)
                    admin_id = group_manager.GroupManager.get_group_admin(self, client_id)
                    user_id_to_remove = self.get_user_id(user_to_remove)

                    if admin_id != client_id:
                        client_socket.send(bytes(f"You are not the owner of the group {group_to_remove}", "utf8"))
                    elif not user_id_to_remove:
                        client_socket.send(bytes("This user does not exist", "utf8"))
                    elif not group_id:
                        client_socket.send(bytes("This group does not exist", "utf8"))
                    elif not self.user_in_group(user_id_to_remove, group_id):
                        client_socket.send(bytes("This user is not in your group", "utf8"))
                    else:
                        if group_manager.GroupManager.remove_user_from_group(self, group_id, user_id_to_remove):
                            client_socket.send(bytes(f"User was successfully removed from the group {group_to_remove}", "utf8"))
                        else:
                            client_socket.send(bytes("You cannot remove yourself of your group you need to leave your group", "utf8"))

                except (IndexError, UnicodeDecodeError):
                    client_socket.send(bytes("An error occurred while adding user to group", "utf8"))

            if received_data.startswith("!leave_group") and client_login:
                user_to_leave_data = client_socket.recv(512)
                user_to_leave_data = user_to_leave_data.decode("utf8")
                try:
                    parts = user_to_leave_data.split("|")
                    group_to_leave = parts[0]
                    next_admin = parts[1]
                    user_id = parts[2]
                    group_id = self.get_existing_group_id_by_name(group_to_leave)
                    leave_group_user_id = self.get_user_id(user_id)
                    next_admin_id = self.get_user_id(next_admin)
                    admin_in_group = self.user_in_group(next_admin_id, group_id)

                    if admin_in_group:
                        if group_id and leave_group_user_id:
                            group_manager.GroupManager.leave_group(self, group_id, leave_group_user_id, next_admin_id)
                            client_socket.send(bytes("You successfully leaved the group", "utf8"))
                        else:
                            client_socket.send(bytes("An error occurred while leaving the group", "utf8"))
                    else:
                        client_socket.send(bytes("The next admin is not in your group or the account does not exist", "utf8"))

                except (IndexError, UnicodeDecodeError):
                    client_socket.send(bytes("An error occurred while leaving the group", "utf8"))

            if received_data.startswith("!get_group_members") and client_login:
                group_to_get_members_from = client_socket.recv(512)
                group_to_get_members_from = group_to_get_members_from.decode("utf8")
                try:
                    parts = group_to_get_members_from.split("|")
                    group = parts[0]
                    client_id = parts[1]
                    group_id = self.get_existing_group_id_by_name(group)

                    if self.user_in_group(client_id, group_id):
                        group_members = group_manager.GroupManager.get_group_members_id(self, group_id)
                        members = ""
                        for member in group_members:
                            member = str(member).strip("(), ")
                            username = self.get_username(member)
                            members = members + f"{username}|"
                        client_socket.send(bytes(members, "utf8"))
                    else:
                        client_socket.send(bytes("You are not in this group or this group does not exist", "utf8"))

                except (IndexError, UnicodeDecodeError):
                    client_socket.send(bytes("An error occurred while leaving the group", "utf8"))

            if received_data.startswith("!get_user_groups") and client_login:
                client_id = client_socket.recv(512)
                client_id = client_id.decode("utf8")
                try:
                    groups = group_manager.GroupManager.get_user_groups(self, client_id)
                    print(groups)
                    group_list = ""
                    for group in groups:
                        group = str(group).strip("(), ")
                        group_name = self.get_group_name(group)
                        print(group_name)
                        group_list = group_list + f"{group_name}|"

                    print(group_list)
                    client_socket.send(bytes(group_list, "utf8"))

                except (IndexError, UnicodeDecodeError):
                    client_socket.send(bytes("An error occurred while leaving the group", "utf8"))
            # have to be overworked
            if received_data.startswith("!group_chat") and client_login:
                group_to_send_data = client_socket.recv(512)
                group_to_send_data = group_to_send_data.decode("utf8")
                parts = group_to_send_data.split("|")
                if len(parts) == 2:
                    group_name = parts[0]
                    user_id = parts[1]
                    group_id = self.get_existing_group_id_by_name(group_name)
                    if self.user_in_group(user_id, group_id):
                        client_socket.send(bytes(f"!groupChat", "utf8"))
                        while True:
                            msg = client_socket.recv(512)
                            message = msg.decode("utf-8")
                            if msg == "!exit":
                                break
                            group_manager.GroupManager.insert_group_message(self, user_id, group_id, message)
                            self.send_message_to_target(group_manager.GroupManager.get_group_members_id(self, group_id), user_id, message)
                            if self.check_client_is_online(client_socket, message):
                                pass
                            else:
                                break
                    else:
                        client_socket.send("You are not in this group.")
                else:
                    client_socket.send("An error occurred while sending the message.")

            if received_data.startswith("!delete_group") and client_login:
                pass

            self.check_client_is_online(client_socket, received_data)

    def get_group_name(self, group_id):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT group_name FROM GroupChats WHERE group_id = %s", (group_id,))
            group_name = self.mycursor.fetchone()
            if group_name is not None:
                return str(group_name).strip("(),' ")
            else:
                return False
        finally:
            lock.release()

    def user_in_group(self, user_id, group_id):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT user_id FROM GroupMembers WHERE user_id = %s AND group_id = %s", (user_id, group_id))
            result = self.mycursor.fetchone()
            return result is not None
        finally:
            lock.release()

    def get_existing_group_id_by_name(self, group_name):
        # Only use when the group already exists
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT group_id FROM GroupChats WHERE group_name = %s", (group_name,))
            group_id = self.mycursor.fetchone()
        finally:
            lock.release()

        if group_id is not None:
            return str(group_id).strip("(), ")
        else:
            return False

    def handle_client_login(self, client_socket, json_data):
        client_id = self.get_user_id(json_data["username"])
        client_socket.send(bytes(str(client_id), "utf8"))
        lock = threading.Lock()
        lock.acquire()
        self.clients.update({client_id: client_socket})
        self.client_id[client_socket] = client_id
        lock.release()

    def check_client_is_online(self, client_socket, msg):
        if not msg:
            client_id = self.client_id[client_socket]
            del self.clients[client_id]
            client_socket.close()
            return False
        else:
            return True

    def get_chat_history(self, client_id, other_client_id):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute(
                "SELECT receiver_id, sender_id, message FROM ChatHistory WHERE (receiver_id = %s AND sender_id = %s) OR (receiver_id = %s AND sender_id = %s) ORDER BY id DESC LIMIT 15",
                (client_id, other_client_id, other_client_id, client_id))
            chat_history = self.mycursor.fetchall()
        finally:
            lock.release()

        return chat_history

    def overwrite_client_adress(self, client_adress, username):
        lock = threading.Lock()
        lock.acquire()
        self.mycursor.execute("UPDATE Users SET ip = %s, port = %s WHERE username = %s", (client_adress[0], client_adress[1], username))
        self.mydb.commit()
        lock.release()

    def check_login_credentials(self, username, password):
        lock = threading.Lock()
        lock.acquire()
        while True:
            try:
                self.mycursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
                result = self.mycursor.fetchone()

            except mysql.connector.errors.OperationalError:
                continue
            else:
                return result is not None
            finally:
                lock.release()

    def is_user_registered(self, username):
        lock = threading.Lock()
        lock.acquire()
        self.mycursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
        result = self.mycursor.fetchone()
        lock.release()
        return result is not None

    def register_in_db(self, user_credentials, client_adress):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("INSERT INTO Users (username, password, ip, port) VALUES (%s, %s, %s, %s)",
                                  (user_credentials["username"], user_credentials["password"], client_adress[0], client_adress[1]))
            self.mydb.commit()
        finally:
            lock.release()

    def get_chat_member_ids(self, target_username, username):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT id FROM Users WHERE username = %s", (target_username,))
            receiver_user_id = self.mycursor.fetchone()

            self.mycursor.execute("SELECT id FROM Users WHERE username = %s", (username,))
            sender_id = self.mycursor.fetchone()
        finally:
            lock.release()

        ids = [receiver_user_id, sender_id]
        return ids

    def get_user_id(self, username):
        lock = threading.Lock()

        try:
            lock.acquire()
            self.mycursor.execute("SELECT id FROM Users WHERE username = %s", (username,))
            identifier = self.mycursor.fetchone()
        finally:
            lock.release()

        if identifier is not None:
            identifier = str(identifier).strip("(), ")
            return int(identifier)
        else:
            return False

    def send_message_to_target(self, receiver_ids, sender_id, message):
        try:
            username = self.get_username(sender_id)
            if not username:
                return False
            for i in receiver_ids:
                receiver = self.clients[i]
                receiver.send(bytes(f"{username}:{message}", "utf8"))
        except KeyError:
            print("User is not online")

    def get_username(self, client_id):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT username FROM Users WHERE id = %s", (client_id,))
        finally:
            lock.release()
        username = self.mycursor.fetchone()
        username = str(username).strip("(),' ")
        print(username)
        if username is None:
            return False
        else:
            return username

    def insert_chat_message(self, receiver_id, sender_id, message):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("INSERT INTO ChatHistory (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                                  (sender_id, receiver_id, message))
            self.mydb.commit()
        finally:
            lock.release()
        self.send_message_to_target([receiver_id], sender_id, message)

    
if __name__ == "__main__":
    server = Server()
    server.start_server()
    while True:
        commands = input("Type stop to stop the server")
        if commands == "stop":
            quit()
