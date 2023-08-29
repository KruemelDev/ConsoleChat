import socket
import mysql.connector
import threading


class GroupManager:

    def __init__(self):
        pass

    def create_group(self, group_name, admin_username):
        pass
        # Create a new group with the given name and add the admin to it

    def add_user_to_group(self, group_name, username):
        pass
        # Add a user to a group

    def remove_user_from_group(self, group_name, username):
        pass
        # Remove a user from a group

    def get_group_members(self, group_name):
        pass
        # Get a list of members in a group

    def get_user_groups(self, username):
        pass
        # Get a list of groups a user is a member of

    def send_group_message(self, group_name, sender_username, message):
        pass
        # Send a message to all members of a group

    def delete_group(self, group_name):
        pass
        # Delete a group and remove all members
