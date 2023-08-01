import socket
import mysql.connector
import threading
import json
import time


class Server:
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            port="3308",
            user="root",
            passwd="spit-preface-inflict-nonsense-hooves-heaven-noted-pitcher-skyway-choice"
        )

        self.mycursor = self.mydb.cursor(buffered=True)
        self.mycursor.execute("CREATE DATABASE IF NOT EXISTS consolechat")
        self.mycursor.execute("USE consolechat")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS Users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), ip VARCHAR(255), port INT(255))")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS ChatStorage (id INT AUTO_INCREMENT PRIMARY KEY, receiver_id INT, sender_id INT, message VARCHAR(512))")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS ChatHistory (id INT AUTO_INCREMENT PRIMARY KEY, receiver_id INT, sender_id INT, message VARCHAR(512))")
        self.set_auto_increment_start_value(100000)
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('192.168.66.58', 12345)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(6)

        self.register_process = False
        self.signin_process = False
        self.target_message_process = False

    def start_server(self):
        while True:
            client_socket, client_adress = self.server_socket.accept()
            print(f"Connection established from {client_adress}")
            self.clients[client_socket] = client_adress
            print(self.clients)

            handle_process = threading.Thread(target=self.handle_client, args=(client_socket, client_adress))
            handle_process.start()

    def handle_client(self, client_socket, client_adress):
        self.clients[client_socket] = client_adress
        print(self.clients)
        while True:
            msg = client_socket.recv(1024)
            print(msg)
            if not msg:
                break
            print(f"Received message from {client_adress}: {msg.decode('utf-8')}")

            received_data = msg.decode('utf-8')
            if received_data.startswith("!signin") or self.signin_process:
                if received_data.startswith("!signin"):
                    self.signin_process = True
                    continue
                json_data = json.loads(received_data)
                print(json_data)
                self.signin_process = False
                print("Das angekommende passwort ist: ",json_data["password"])
                print("Der angekommende benutzername ist: ", json_data["username"])
                if self.check_login_credentials(json_data["username"], json_data["password"]):
                    client_socket.send(bytes("!successful", "utf8"))
                    self.overwrite_client_adress(client_adress, json_data["username"])
                else:
                    client_socket.send(bytes("!login failed", "utf8"))

            if received_data.startswith("!register") or self.register_process:
                if received_data.startswith("!register"):
                    self.register_process = True
                    continue
                json_data = json.loads(received_data)
                print(json_data)
                self.register_process = False
                if self.is_user_registered(json_data["username"]):
                    client_socket.send(bytes("!already taken", "utf8"))
                else:
                    store_thread = threading.Thread(target=self.register_in_db, args=(json_data, client_adress))
                    store_thread.start()
                    client_socket.send(bytes("!successful", "utf8"))

            print(received_data)
            if received_data.startswith("!chat") or self.target_message_process:
                print(received_data)
                if received_data.startswith("!chat"):
                    self.target_message_process = True
                    continue
                self.target_message_process = False
                print(received_data)
                if self.is_user_registered(received_data):
                    client_socket.send(bytes("!user exists", "utf8"))
                    chat_members = client_socket.recv(1024)
                    chat_members_decoded = chat_members.decode("utf-8")
                    chat_members_parts = chat_members_decoded.split("|")

                    target_username = chat_members_parts[0]
                    print(target_username)
                    username = chat_members_parts[1]
                    ids = self.get_chat_member_ids(target_username, username)
                    target_id = ids[0]
                    client_id = ids[1]
                    client_socket.send(bytes(f"{target_id}|{client_id}", "utf8"))
                else:
                    client_socket.send(bytes("!user doesnt exist", "utf8"))
                    continue

                while True:
                    msg = client_socket.recv(512)
                    msg_decoded = msg.decode("utf-8")
                    parts = msg_decoded.split("|")
                    receiver_id = int(parts[0].strip("()").rstrip(','))
                    client_id = int(parts[1].strip("()").rstrip(','))
                    message = parts[2]
                    self.insert_chat_message(receiver_id, client_id, message, client_socket)

    def set_auto_increment_start_value(self, start_value):
        query = f"ALTER TABLE Users AUTO_INCREMENT = {start_value};"
        self.mycursor.execute(query)

    def overwrite_client_adress(self, client_adress, username):
        self.mycursor.execute("UPDATE Users SET ip = %s, port = %s WHERE username = %s", (client_adress[0], client_adress[1], username))
        self.mydb.commit()

    def check_login_credentials(self, username, password):
        self.mycursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        result = self.mycursor.fetchone()
        return result is not None

    def is_user_registered(self, username):
        self.mycursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
        result = self.mycursor.fetchone()
        return result is not None

    def get_chat_member_ids(self, target_username, username):
        print(target_username)
        self.mycursor.execute("SELECT id FROM Users WHERE username = %s", (target_username,))
        receiver_user_id = self.mycursor.fetchone()
        print(receiver_user_id)
        self.mycursor.execute("SELECT id FROM Users WHERE username = %s", (username,))
        sender_id = self.mycursor.fetchone()
        print(receiver_user_id)
        ids = [receiver_user_id, sender_id]
        return ids

    def register_in_db(self, user_credentials, client_adress):
        print(user_credentials["password"])
        self.mycursor.execute("INSERT INTO Users (username, password, ip, port) VALUES (%s, %s, %s, %s)",
                              (user_credentials["username"], user_credentials["password"], client_adress[0], client_adress[1]))
        self.mydb.commit()

    def send_message_to_target(self, sender_id, receiver_id, client_socket):
        while True:
            self.mycursor.execute("SELECT message FROM ChatStorage WHERE receiver_id = %s", (sender_id,))
            message_to_send = self.mycursor.fetchone()
            if message_to_send is None:
                time.sleep(1.5)
                continue
            else:
                try:
                    client_socket.send(bytes(str(message_to_send), "utf8"))
                    self.mycursor.execute("INSERT INTO ChatHistory (sender_id, receiver_id, message) SELECT sender_id, receiver_id, message FROM ChatStorage WHERE receiver_id = %s", (receiver_id,))
                    self.mycursor.execute("DELETE FROM ChatStorage WHERE receiver_id = %s;", (sender_id,))
                    self.mydb.commit()
                    time.sleep(1.5)
                except Exception:
                    pass

    def insert_chat_message(self, receiver_id, sender_id, message, client_socket):
        self.mycursor.execute("INSERT INTO ChatStorage (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                              (sender_id, receiver_id, message))
        self.mydb.commit()
        message_to_target_thread = threading.Thread(target=self.send_message_to_target, args=(sender_id, receiver_id, client_socket))
        message_to_target_thread.start()


if __name__ == "__main__":
    server = Server()
    server.start_server()
    while True:
        commands = input("Type stop to stop the server")
        if commands == "stop":
            quit()
