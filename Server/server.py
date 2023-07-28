import socket
import mysql.connector
import threading
import json


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
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS ChatHistory (senderid INT, receiverid INT, message VARCHAR(255))")
        self.set_auto_increment_start_value(100000)
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 12345)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)

        self.register_process = False
        self.signin_process = False
        self.target_message_process = False

    def start_server(self):
        while True:
            client_socket, client_adress = self.server_socket.accept()
            print(f"Connection established from {client_adress}")
            self.clients[client_socket] = client_adress
            print(self.clients)
            handle_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_adress))
            handle_thread.start()

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
                else:
                    client_socket.send(bytes("!user doesnt exist", "utf8"))
                    continue

                while True:
                    msg = client_socket.recv(1024).decode("utf-8")
                    parts = msg.split("|")
                    sender_id = parts[0]
                    receiver_id = parts[1]
                    message_to_send = "|".join(parts[2:])

    def set_auto_increment_start_value(self, start_value):
        query = f"ALTER TABLE Users AUTO_INCREMENT = {start_value};"
        self.mycursor.execute(query)

    def overwrite_client_adress(self, client_adress, username):
        self.mycursor.execute("UPDATE Users SET ip = %s, port = %s WHERE username = %s", (client_adress[0], client_adress[1], username))
        self.mydb.commit()

    def check_login_credentials(self, username, password):
        sql_query = "SELECT * FROM Users WHERE username = %s AND password = %s"
        print("Ausgeführte SQL-Abfrage:", sql_query, (username, password))
        self.mycursor.execute(sql_query, (username, password))
        result = self.mycursor.fetchone()
        return result is not None

    def is_user_registered(self, username):
        self.mycursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
        result = self.mycursor.fetchone()
        return result is not None

    def register_in_db(self, user_credentials, client_adress):
        print(user_credentials["password"])
        self.mycursor.execute("INSERT INTO Users (username, password, ip, port) VALUES (%s, %s, %s, %s)",
                              (user_credentials["username"], user_credentials["password"], client_adress[0], client_adress[1]))
        self.mydb.commit()


if __name__ == "__main__":
    server = Server()
    server.start_server()

# This just works for one person at once at the moment
