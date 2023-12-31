import socket
import threading
import hashlib
import json
import ast
import multiprocessing


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
                    client_id = self.client_socket.recv(512)
                    client_id_decoded = client_id.decode("utf-8")
                    menu_thread = threading.Thread(target=self.login_menu, args=(username_input, client_id_decoded))
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
                    print(server_answer.strip("!"))
                    continue
                elif server_answer == "!successful":
                    client_id = self.client_socket.recv(512)
                    client_id_decoded = client_id.decode("utf-8")
                    print("Your account has been created")
                    menu_thread = threading.Thread(target=self.login_menu, args=(username_input, client_id_decoded))
                    menu_thread.start()
                    break
            elif check_account == "!quit":
                quit()
            else:
                continue

    def login_menu(self, username, client_id):
        print("Type !exit to return to menu")

        while True:
            commands = input("Type help to see all commands: ")
            if commands == "help":
                print("Type: \n"
                      "help - list all commands\n"
                      "chat - chat with a single person\n"
                      "createGroup - create a group for a groupChat\n"
                      "addUser - adds a user to your group\n"
                      "removeUser - removes a user of your group\n"
                      "leaveGroup - leave a group\n"
                      "groupMember - prints all members in your group\n"
                      "groups - prints all groups you are in")

            elif commands == "chat":
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
                            client_id = chat_member_ids_parts[1]
                            self.client_socket.send(bytes(target_id, "utf8"))
                            self.chat(target_username, target_id, client_id, username, 0)
                        else:
                            print("Sorry, this user does not exist, please enter another user name")
                            break
                    elif target_username == "!exit":
                        break

                    else:
                        continue
                continue

            elif commands == "createGroup":
                for i in range(2):
                    print()
                self.client_socket.send(bytes("!create_group", "utf8"))
                group_name = input("Specify a name for the group: ")

                self.client_socket.send(bytes(f"{group_name}|{username}", "utf8"))
                answer = self.client_socket.recv(512)
                answer_decoded = answer.decode("utf8")
                print(answer_decoded)

            elif commands == "addUser":
                self.client_socket.send(bytes("!add_user_to_group", "utf8"))
                user = input("Which user do you want to add to your group: ")
                group_to_add_user = input(f"In which group do you want to add {user}: ")

                user_to_add_data = f"{user}|{group_to_add_user}|{client_id}"
                self.client_socket.send(bytes(user_to_add_data, "utf8"))
                answer = self.client_socket.recv(512)
                print(answer.decode("utf8"))

            elif commands == "removeUser":
                self.client_socket.send(bytes("!remove_user_from_group", "utf8"))
                user = input("Which user do you want to remove from your group: ")
                group_to_remove_user = input(f"In which group do you want to delete {user}: ")

                user_to_remove_data = f"{user}|{group_to_remove_user}|{client_id}"
                self.client_socket.send(bytes(user_to_remove_data, "utf8"))
                answer = self.client_socket.recv(512)
                print(answer.decode("utf8"))

            elif commands == "leaveGroup":
                self.client_socket.send(bytes("!leave_group", "utf8"))
                group_to_leave = input("Which group do you want to leave: ")
                next_admin = input("Who should become the next admin of the group?")
                leave_group_data = f"{group_to_leave}|{next_admin}|{client_id}"
                self.client_socket.send(bytes(leave_group_data, "utf8"))
                answer = self.client_socket.recv(512)
                print(answer.decode("utf8"))

            elif commands == "groupMember":
                self.client_socket.send(bytes("!get_group_members", "utf8"))
                group_to_get_members = input("Of which group do you want to get the members: ")
                group_to_get_members_data = f"{group_to_get_members}|{client_id}"
                self.client_socket.send(bytes(group_to_get_members_data, "utf8"))
                answer = self.client_socket.recv(512)
                answer = answer.decode("utf8")
                if "|" in answer:
                    members = answer.split("|")
                    print(f"Your group has {len(members) - 1} members.")
                    print("In your group are these members:")

                    for member in members:
                        print(member)
                else:
                    print(answer)

            elif commands == "groups":
                self.client_socket.send(bytes("!get_user_groups", "utf8"))
                self.client_socket.send(bytes(client_id, "utf8"))
                answer = self.client_socket.recv(512)
                answer = answer.decode("utf8")
                if "|" in answer:
                    groups = answer.split("|")
                    print(f"Your are in {len(groups) - 1} groups.")
                    print("You have these groups:")

                    for group in groups:
                        print(group)
                else:
                    print(answer)

            elif commands == "groupChat":
                self.client_socket.send(bytes("!group_chat", "utf8"))
                chat_group = input("In which group do you want to send messages: ")
                self.client_socket.send(bytes(f"{chat_group}|{client_id}", "utf8"))
                answer = self.client_socket.recv(512)
                answer = answer.decode("utf8")

                if answer == "!groupChat":
                    chat_data = self.client_socket.recv(256)
                    chat_data = chat_data.decode("utf8").split("|")

                    group_name = chat_data[0]
                    group_id = chat_data[1]
                    self.chat(group_name, group_id, client_id, username, group_id)
                else:
                    print("antwort: " + answer)
            elif commands == "!quit":
                quit()
            else:
                continue

    def chat(self, chat_target_name, target_id, client_id, username, group_id):
        print("This is a chat with:", chat_target_name)
        for i in range(5):
            print("")
        if int(group_id) == 0:
            self.receive_and_display_chat_history(client_id, chat_target_name)
        elif int(group_id) > 0:
            self.receive_and_display_chat_history_group(client_id)

        receive_target_messages_process = multiprocessing.Process(target=self.recv_messages, args=(chat_target_name, group_id, username))
        receive_target_messages_process.start()
        while True:
            message = input(f"You to {chat_target_name}: ")
            if message == "":
                continue
            if message.startswith("!exit"):
                receive_target_messages_process.terminate()
                self.client_socket.send(bytes("!exit", "utf8"))
                break
            else:
                try:
                    self.client_socket.send(bytes(f"{target_id}|{client_id}|{message}", "utf8"))
                except BrokenPipeError:
                    continue

        self.login_menu(username, client_id)

    def recv_messages(self, chat_target_name, group_id, username):
        while True:
            try:

                chat_message = self.client_socket.recv(640)
                chat_message_decoded = chat_message.decode("utf8")
                split_message = chat_message_decoded.split(":")
                group_id_data = split_message[0]
                message_owner = split_message[1]
                message = split_message[2]
                group_name = split_message[3]
                if not chat_message or chat_message == "!error":
                    print("Disconnected")
                    break
                if chat_message_decoded == "":
                    continue

                if message_owner == username:
                    continue
                if str(message_owner) == str(chat_target_name) and int(group_id_data) == 0:
                    print(f"\n{message_owner}: {message}")
                elif message_owner != chat_target_name and int(group_id_data) == 0:
                    for i in range(1):
                        print("")
                    print(message_owner, "has sent you a message")
                    for i in range(1):
                        print("")
                    continue

                if group_id == group_id_data:
                    print(f"\n{message_owner}: {message}")
                elif group_id != 0:
                    print("A message was sent in " + group_name)

            except ConnectionResetError:
                print("Cant connect to server")
                continue

    @staticmethod
    def reverse_list(input_list):
        reverse_list = input_list[::-1]
        return reverse_list

    def receive_and_display_chat_history_group(self, group_id):
        chat_history = self.client_socket.recv(8192)
        chat_history_decoded = chat_history.decode("utf-8")
        eval_list = ast.literal_eval(chat_history_decoded)
        chat_history_list = [[tup for tup in item] for item in eval_list]
        reverse_chat_history_list = self.reverse_list(chat_history_list)

        for i in reverse_chat_history_list:
            print(i[0] + ": " + i[1])

    def receive_and_display_chat_history(self, client_id, chat_target_name):
        chat_history = self.client_socket.recv(8192)
        chat_history_decoded = chat_history.decode("utf-8")
        print(chat_history_decoded)
        eval_list = ast.literal_eval(chat_history_decoded)
        chat_history_list = [[tup for tup in item] for item in eval_list]
        reverse_chat_history_list = self.reverse_list(chat_history_list)

        for i in reverse_chat_history_list:
            striped_client_id = client_id.strip("(),")

            if str(striped_client_id) == str(i[1]):
                print(f"You to {chat_target_name}: {i[2]}")
            elif str(striped_client_id) == str(i[0]):
                print(f"{chat_target_name}: {i[2]}")


if __name__ == "__main__":
    client = Client()
    login_thread = threading.Thread(target=client.login())
    login_thread.start()
    login_thread.join()
