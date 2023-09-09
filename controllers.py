from database import Database
from models import UserData
from dataclasses import asdict


class UserController:
    def __init__(self, database: Database, *args, **kwargs):
        self.database = database

    def get_user(self, _id: int):
        pass

    def get_all_users(self):
        return [UserData(*i) for i in self.database.get_all_users()]

    def create_user(self, user: UserData):
        if not self.check_user_exists(user.id):
            return self.database.create_user(**asdict(user))
        return self.database.update_user(**asdict(user))

    def check_user_exists(self, _id: int):
        return self.database.user_exists(_id)


class EventController:
    def __init__(self, database: Database, *args, **kwargs):
        self.database = database


