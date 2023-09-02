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
        self.mycursor.execute("USE consolechat")

    def create_group(self, group_name: str, admin_id: int) -> bool:
        lock = threading.Lock()
        try:
            lock.acquire()
            print(group_name)
            self.mycursor.execute("INSERT INTO GroupChats (group_name, group_admin_id) VALUES (%s, %s)", (group_name, admin_id))
            self.mydb.commit()
        finally:
            lock.release()
        return True

    def add_user_to_group(self, group_id: int, user_id_to_add: int):
        lock = threading.Lock()
        try:
            lock.acquire()

            self.mycursor.execute("INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)", (group_id, user_id_to_add))
            self.mydb.commit()
        finally:
            lock.release()
        return True

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

