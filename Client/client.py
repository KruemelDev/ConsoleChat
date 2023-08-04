import socket
import threading
import hashlib
import json


class Client:
    def __init__(self):
        ip = input("Enter the ip adress of your server: ")
        while True:
            port = input("Enter the port where the socket is running: ")
            try:
                self.port_to_int = int(port)
                if self.port_to_int < 65535:
                    break
                elif self.port_to_int > 1023:
                    continue
            except ValueError as e:
                print(e)
        while True:
            try:

                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_address = (ip, self.port_to_int)
                self.client_socket.connect(self.server_address)
                break
            except ConnectionRefusedError:
                print("Connection refused")
                quit()
        self.running = True
        self.long_message = ""

    @staticmethod
    def hash_password(password):
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        return hashed_password

    def send_to_server_user_credentials(self, username, password):
        hashed_password = self.hash_password(password)
        login_data = {"username": username, "password": hashed_password}
        json_data = json.dumps(login_data)
        self.client_socket.send(json_data.encode("utf8"))

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
                    target_username = input("Which user would you like to write with: ")
                    if target_username == "!quit":
                        quit()
                    if not target_username == "" or None:

                        self.client_socket.send(bytes(target_username, "utf-8"))
                        server_answer = self.client_socket.recv(1024).decode("utf-8")
                        if server_answer == "!user exists":
                            chat_members = f"{target_username}|{username}"
                            self.client_socket.send(bytes(chat_members, "utf8"))

                            chat_ids = self.client_socket.recv(1024)
                            chat_member_ids_decoded = chat_ids.decode("utf-8")
                            chat_member_ids_parts = chat_member_ids_decoded.split("|")

                            target_id = chat_member_ids_parts[0]
                            sender_id = chat_member_ids_parts[1]
                            self.chat(target_username, target_id, sender_id, username)
                        else:
                            print("Sorry, this user does not exist, please enter another user name")
                            break
                    elif target_username == "!exit":
                        break

                    else:
                        continue
                # Return to menu
                continue
            elif commands == "!quit":
                quit()
            else:
                continue

    def chat(self, chat_target_name, target_id, sender_id, username):
        print("This is a chat with:", chat_target_name)
        for i in range(20):
            print("")
        receive_target_messages_thread = threading.Thread(target=self.recv_messages, args=(chat_target_name,))
        receive_target_messages_thread.start()

        while self.running:
            if self.running:
                message = input(f"You to {chat_target_name}: ")
                if message == "":
                    continue
                if message.startswith("!exit"):
                    self.running = False
                try:
                    self.client_socket.send(bytes(f"{target_id}|{sender_id}|{message}", "utf8"))
                except BrokenPipeError:
                    continue

        print("Please wait a few seconds, the chat will then close")
        receive_target_messages_thread.join()
        self.login_menu(username)

    def recv_messages(self, chat_target_name):
        while self.running:
            try:

                chat_message = self.client_socket.recv(640)
                chat_message_decoded = chat_message.decode("utf8")
                if not chat_message:
                    print("Disconnected")
                    break
                if chat_message_decoded == "":
                    continue
                if chat_message_decoded.startswith("server: "):
                    print(f"\n{chat_message_decoded}")
                    continue
                if chat_message_decoded:
                    print(f"\n{chat_target_name}: {chat_message_decoded}")
            except socket.timeout:
                pass


if __name__ == "__main__":
    client = Client()
    login_thread = threading.Thread(target=client.login())
    login_thread.start()
    login_thread.join()
