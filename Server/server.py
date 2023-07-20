import socket
import mysql.connector
import threading

mydb = mysql.connector.connect(
    host="localhost",
    port="3308",
    user="root",
    passwd="spit-preface-inflict-nonsense-hooves-heaven-noted-pitcher-skyway-choice"
)


class Server:
    def __init__(self):
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("CREATE DATABASE IF NOT EXISTS consolechat")
        mycursor.execute("USE consolechat")
        mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), ip VARCHAR(255), port INT(255))".format("Users"))

        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 5050)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)

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
            store_thread = threading.Thread(target=self.store_in_db())
            store_thread.start()
            print(f"Received message from {self.client_address}: {self.msg.decode('utf-8')}")

    def store_in_db(self):
        if self.msg.decode('utf-8') == "register":
            if self.msg.decode('utf-8')[::]:
                pass

if __name__ == "__main__":
    server = Server()
    main_thread = threading.Thread(target=server.main())
    main_thread.start()
