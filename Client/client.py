import socket
import threading
import bcrypt


class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 5050)
        self.client_socket.connect(self.server_address)

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def login(self):
        while True:
            check_account = input("Do you already have an account? If you have one type: signin else type: register.")
            if check_account == "signin":
                print()
                self.client_socket.send(bytes("signin", "utf8"))

                username = input("Type your username")
                password = input("Type your password")

                hashed_password = self.hash_password(password)
                account_data = (username, hashed_password)
                self.client_socket.send(bytes("Sign in with{}".format(account_data), "utf8"))
                break
            elif check_account == "register":
                print()
                self.client_socket.send(bytes("register", "utf8"))

                username = input("Type a name how your friends will see you")
                password = input("Type a password")

                hashed_password = self.hash_password(password)
                register_data = (username, hashed_password)
                self.client_socket.send(bytes("Register with {}".format(register_data), "utf8"))
                break
            else:
                continue


if __name__ == "__main__":
    client = Client()
    login_thread = threading.Thread(target=client.login())
    login_thread.start()
    login_thread.join()
