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
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), ip VARCHAR(255), port INT(255))".format("Users"))

        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 12345)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)

        self.register_process = False
        self.signin_process = False

    def main(self):
        print("i am in main")
        while True:
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"Connection established from {self.client_address}")
            self.clients[self.client_socket] = self.client_address
            print(self.clients)
            handle_thread = threading.Thread(target=self.handle_client)
            handle_thread.start()

    def handle_client(self):
        self.clients[self.client_socket] = self.client_address
        print(self.clients)
        while True:
            self.msg = self.client_socket.recv(1024)
            print(self.msg)
            if not self.msg:
                # Client disconnected
                break

            print(f"Received message from {self.client_address}: {self.msg.decode('utf-8')}")

            received_data = self.msg.decode('utf-8')
            if received_data.startswith("!signin") or self.signin_process:
                if received_data.startswith("!signin"):
                    self.signin_process = True
                    continue
                json_data = json.loads(received_data)
                print(json_data)
                self.signin_process = False

            if received_data.startswith("!register") or self.register_process:
                if received_data.startswith("!register"):
                    self.register_process = True
                    continue
                json_data = json.loads(received_data)
                print(json_data)
                self.register_process = False
                if self.is_user_registered(json_data["username"]):
                    self.client_socket.send(bytes("!Already taken", "utf8"))
                else:

                    # Args cannot be overgiven
                    store_thread = threading.Thread(target=self.register_in_db(), args=(json_data))
                    self.client_socket.send(bytes("!Successful", "utf8"))

                # store_thread = threading.Thread(target=self.store_in_db())
                # store_thread.start()

    def is_user_logged_in(self):
        pass

    def is_user_registered(self, username):
        self.mycursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
        result = self.mycursor.fetchone()
        return result is not None

    def register_in_db(self, user_credentials):
        self.mycursor.execute("INSERT INTO Users (username, password, ip, port) VALUES (%s, %s, %s, %s)",
                              (user_credentials["username"], user_credentials["password"], self.client_address[0], self.client_address[1]))
        self.mydb.commit()


if __name__ == "__main__":
    server = Server()
    main_thread = threading.Thread(target=server.main())
    main_thread.start()

# This just works for one person at once at the moment
