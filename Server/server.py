import socket
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    port="3308",
    user="root",
    passwd="spit-preface-inflict-nonsense-hooves-heaven-noted-pitcher-skyway-choice"
)


def main():
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("CREATE DATABASE IF NOT EXISTS consolechat")
    mycursor.execute("USE consolechat")
    mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))".format("Users"))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 5050)
    server_socket.bind(server_address)
    server_socket.listen(5)


if __name__ == "__main__":
    main()
