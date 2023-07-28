import socket
import threading
import hashlib
import json


class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 12345)
        self.client_socket.connect(self.server_address)
        self.running = True

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
        print("Type !quit to quit the program")
        while True:
            check_account = input("Do you already have an account? If you have one type: signin else type: register: ")
            if check_account == "signin":
                print()
                self.client_socket.send(bytes("!signin", "utf8"))

                username_input = input("Type your username: ")
                password_input = input("Type your password: ")
                if username_input == "!quit" or password_input == "!quit":
                    quit()
                self.send_to_server_user_credentials(username_input, password_input)
                server_answer = self.client_socket.recv(1024).decode("utf-8")
                print(server_answer)

                if server_answer == "!successful":
                    print("You are logged in")
                    menu_thread = threading.Thread(target=self.login_menu, args=(username_input,))
                    menu_thread.start()
                    break
                elif server_answer == "!login failed":
                    print("Your login failed. Please try again")
                    continue
                break
            elif check_account == "register":
                print()
                self.client_socket.send(bytes("!register", "utf8"))
                username_input = input("Type a name how your friends will see you: ")

                while username_input == "!exit":
                    username_input = input("Type a name how your friends will see you: ")
                password_input = input("Type a password: ")
                if username_input == "!quit" or password_input == "!quit":
                    quit()
                self.send_to_server_user_credentials(username_input, password_input)
                server_answer = self.client_socket.recv(1024).decode("utf-8")
                print(server_answer)
                if server_answer == "!already taken":
                    continue
                elif server_answer == "!successful":
                    print("Your account has been created")
                    menu_thread = threading.Thread(target=self.login_menu, args=(username_input,))
                    menu_thread.start()
                    break
            elif check_account == "!quit":
                quit()
            else:
                continue

    def login_menu(self, username):
        print("Type !exit to return to menu")

        while True:
            commands = input("Type chat if you want to chat with a person: ")
            if commands == "chat":
                self.client_socket.send(bytes("!chat", "utf8"))
                while True:
                    user_to_write = input("Which user would you like to write with: ")
                    print(user_to_write)
                    if user_to_write == "!quit":
                        quit()
                    if not user_to_write == "" or None:
                        target = bytes(user_to_write, "utf-8")
                        self.client_socket.send(target)
                        server_answer = self.client_socket.recv(1024).decode("utf-8")
                        print("Server answer:", server_answer)
                        if server_answer == "!user exists":
                            self.chat(user_to_write)
                        else:
                            print("Sorry, this user does not exist, please enter another user name")
                            break
                    elif user_to_write == "!exit":
                        break

                    else:
                        continue
                # Return to menu
                continue
            elif commands == "!quit":
                quit()
            else:
                continue

    def chat(self, chat_target):
        print("This is a chat with: ", chat_target)
        for i in range(20):
            print("")
        receive_target_messages_thread = threading.Thread(target=self.recv_target_messages)
        receive_target_messages_thread.start()
        while self.running:
            message = input("You: ")
            if message.startswith("!exit"):
                self.running = False
            self.client_socket.send(bytes(message, "utf8"))
        print("Please wait a few seconds, the chat will then close")
        receive_target_messages_thread.join()
        self.login_menu()

    def recv_target_messages(self):
        self.client_socket.settimeout(2.5)

        while self.running:
            try:
                chat_message_target = self.client_socket.recv(1024).decode("utf-8")
                yield chat_message_target
            except socket.timeout:
                pass
        self.client_socket.settimeout(None)
        # Due to the timeout, a few messages cannot be received -> dynamic timeout would be the solution


if __name__ == "__main__":
    client = Client()
    login_thread = threading.Thread(target=client.login())
    login_thread.start()
    login_thread.join()
