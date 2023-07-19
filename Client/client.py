import socket


def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 5050)
    client_socket.connect(server_address)

    while True:
        check_account = input("Do you already have an account? If you have one type: signin else type: register.")
        if check_account == "signin":
            print()
            username = input("Type your username")
            password = input("Type your password")
            account_data = (username, password)
            client_socket.send(bytes("Sign in with{}".format(account_data), "utf8"))
        elif check_account == "register":
            print()
            username = input("Type a name how your friends will see you")
            password = input("Type a password")
            register_data = (username, password)
            client_socket.send(bytes("Register with {}".format(register_data), "utf8"))

        else:
            continue

if __name__ == "__main__":
    main()
