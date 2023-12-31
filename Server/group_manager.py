import mysql.connector
import threading


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

    def get_group_admin(self, group_id: int):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT admin_id FROM GroupChats WHERE group_id = %s", (group_id,))
            admin_id = self.mycursor.fetchone()
            admin_id_striped = str(admin_id).strip("(), ")
            if admin_id is not None:
                return admin_id_striped
            else:
                return False
        finally:
            lock.release()

    def create_group(self, group_name: str, admin_id: int) -> bool:
        lock = threading.Lock()
        try:
            lock.acquire()
            print(group_name)
            self.mycursor.execute("SELECT group_name FROM GroupChats WHERE group_name = %s", (group_name,))
            group_name_already_exists = self.mycursor.fetchone()
            if group_name_already_exists is None:
                self.mycursor.execute("INSERT INTO GroupChats (group_name, admin_id) VALUES (%s, %s)", (group_name, admin_id))
                self.mydb.commit()
                user_id = admin_id
                group_id = self.get_group_id_by_name(group_name)
                self.mycursor.execute("INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)", (group_id, user_id))
                self.mydb.commit()
                return True
            else:
                return False
        finally:
            lock.release()

    def get_group_id_by_name(self, group_name: str) -> int:
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT group_id FROM GroupChats WHERE group_name = %s", (group_name,))
            group_id = self.mycursor.fetchone()
            return int(str(group_id).strip("(), "))
        finally:
            lock.release()

    def add_user_to_group(self, group_id: int, user_id_to_add: int):
        lock = threading.Lock()
        try:
            lock.acquire()

            self.mycursor.execute("SElECT user_id FROM GroupMembers WHERE group_id = %s AND user_id = %s", (group_id, user_id_to_add))
            user_in_group = self.mycursor.fetchone()
            if user_in_group is None:
                self.mycursor.execute("INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)", (group_id, user_id_to_add))
                self.mydb.commit()
                return True
            else:
                return False
        finally:
            lock.release()

    def remove_user_from_group(self, group_id: int, user_id_to_remove: int):
        lock = threading.Lock()
        try:
            lock.acquire()
            admin_id = self.get_group_admin(group_id)
            if admin_id == user_id_to_remove:
                return False
            else:
                self.mycursor.execute("DELETE FROM GroupMembers WHERE group_id = %s AND user_id = %s", (group_id, user_id_to_remove))
                self.mydb.commit()
                return True
        finally:
            lock.release()

        # Remove a user from a group

    def leave_group(self, group_id: int, user_id: int, new_admin_id: int):
        lock = threading.Lock()
        try:
            lock.acquire()

            self.mycursor.execute("DELETE FROM GroupMembers WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            self.mydb.commit()

            self.mycursor.execute("UPDATE GroupChats SET admin_id = %s WHERE group_id = %s", (new_admin_id, group_id))
            self.mydb.commit()
        finally:
            lock.release()
        return True

    def get_group_members_id(self, group_id: int) -> list:
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT user_id FROM GroupMembers WHERE group_id = %s", (group_id,))
            members = self.mycursor.fetchall()
            return list(members)
        finally:
            lock.release()

    def get_user_groups(self, user_id: int) -> list:

        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT group_id FROM GroupMembers WHERE user_id = %s", (user_id,))
            groups = self.mycursor.fetchall()
            return groups
        finally:
            lock.release()

    def insert_group_message(self, sender_id: int, group_id: int, message: str):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("INSERT INTO GroupChatHistory (group_id, sender_id, message) VALUES (%s, %s, %s)", (group_id, sender_id, message))
            self.mydb.commit()
        finally:
            lock.release()

    def group_exists(self, group_id):
        lock = threading.Lock()
        try:
            lock.acquire()
            self.mycursor.execute("SELECT * FROM GroupChats WHERE group_id = %s", (group_id,))
            result = self.mycursor.fetchone()
            return result is not None
        finally:
            lock.release()

    def get_chat_history_for_groups(self, group_id):
        lock = threading.Lock()
        try:
            lock.acquire()

            query = """
            SELECT Users.username, GroupChatHistory.message
            From GroupChats
            JOIN GroupMembers ON GroupChats.group_id = GroupMembers.group_id
            JOIN Users ON GroupMembers.user_id = Users.id
            JOIN GroupChatHistory ON GroupChats.group_id = GroupChatHistory.group_id
            WHERE GroupChats.group_id = %s AND Users.id = GroupChatHistory.sender_id
            ORDER BY GroupChatHistory.id DESC LIMIT 30
            """
            self.mycursor.execute(query, (group_id,))
            result = self.mycursor.fetchall()
            print(result)
            return result
        finally:
            lock.release()

    def delete_group(self, group_id: int):
        pass
        # Delete a group and remove all members
