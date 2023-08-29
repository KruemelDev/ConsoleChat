import socket
import mysql.connector
import threading
from typing import Tuple


class GroupManager:

    def __init__(self, db_password: str):
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                port=3308,
                user="root",
                passwd=f"{db_password}"
            )
        except mysql.connector.errors as e:
            print(e)

        self.mycursor = self.mydb.cursor(buffered=True)
        self.mycursor.execute("CREATE DATABASE IF NOT EXISTS consolechat")
        self.mycursor.execute("USE consolechat")

    def create_group(self, group_name: str, admin_id: int) -> bool:
        print(group_name)
        lock = threading.Lock()
        lock.acquire()
        print(group_name)
        self.mycursor.execute("INSERT INTO GroupChats (group_name = %s, admin_id = %s)", (group_name, admin_id))
        self.mydb.commit()
        lock.release()
        return True

    def add_user_to_group(self, group_id: int, user_id: str):
        pass
        # Add a user to a group

    def remove_user_from_group(self, group_id: int, user_id: int):
        pass
        # Remove a user from a group

    def get_group_members(self, group_id: int) -> Tuple:
        pass
        # Get a list of members in a group

    def get_user_groups(self, user_id: int) -> Tuple:
        pass
        # Get a list of groups a user is a member of

    def send_group_message(self, group_id: int, sender_id: int, message: str):
        pass
        # Send a message to all members of a group

    def delete_group(self, group_id: int):
        pass
        # Delete a group and remove all members

