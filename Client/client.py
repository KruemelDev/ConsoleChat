import socket
import threading
import hashlib
import json


class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 12345)
        self.client_socket.connect(self.server_address)

    @staticmethod
    def hash_password(password):
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        return hashed_password

    def send_to_server_user_credentials(self, username, password):
        hashed_password = self.hash_password(password)
        login_data = {"username": username, "password": hashed_password}
        json_data = json.dumps(login_data)
        self.client_socket.send(json_data.encode("utf8"))
        print("Der geesendete benutzer name ist:", login_data["username"])
        print("Der gesendete password name ist:", login_data["password"])


    def login(self):
        while True:
            check_account = input("Do you already have an account? If you have one type: signin else type: register: ")
            if check_account == "signin":
                print()
                self.client_socket.send(bytes("!signin", "utf8"))

                username_input = input("Type your username: ")
                password_input = input("Type your password: ")
                self.send_to_server_user_credentials(username_input, password_input)
                server_answer = self.client_socket.recv(1024).decode("utf-8")
                print(server_answer)

                if server_answer == "!successful":
                    print("You are logged in")
                    threading.Thread(target=self.login_menu, args=(username_input,))
                    break
                elif server_answer == "!login failed":
                    print("Your login failed. Please try again")
                    continue
                break
            elif check_account == "register":
                print()
                self.client_socket.send(bytes("!register", "utf8"))

                username_input = input("Type a name how your friends will see you: ")
                password_input = input("Type a password: ")

                self.send_to_server_user_credentials(username_input, password_input)
                server_answer = self.client_socket.recv(1024).decode("utf-8")
                print(server_answer)
                if server_answer == "!already taken":
                    continue
                elif server_answer == "!successful":
                    print("Your account has been created")
                    menu_thread = threading.Thread(target=self.login_menu(), args=(username_input,))
                    menu_thread.start()
                    break
            else:
                continue

    def login_menu(self):
        pass


if __name__ == "__main__":
    client = Client()
    login_thread = threading.Thread(target=client.login())
    login_thread.start()
    login_thread.join()
