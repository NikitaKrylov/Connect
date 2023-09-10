from database import Database
from models import UserData, EventData
from dataclasses import asdict


class UserController:
    def __init__(self, database: Database, *args, **kwargs):
        self.database = database

    def get_user(self, _id: int):
        data = self.database.get_user(_id)
        if data:
            return UserData(*data)
        return None

    def get_all_users(self):
        return [UserData(*i) for i in self.database.get_all_active_users()]

    def create_user(self, user: UserData):
        if not self.check_user_exists(user.id):
            return self.database.create_user(**asdict(user))
        return self.database.update_user(**asdict(user))

    def check_user_exists(self, _id: int):
        return self.database.user_exists(_id)

    def get_users_langs(self):
        return self.database.get_users_langs()

    def update_user_lang(self, _id: int, lang: str):
        self.database.update_user_lang(_id, lang)

    def change_user_activity(self, _id: int, value: int):
        self.database.change_user_activity(_id, value)



class EventController:
    def __init__(self, database: Database, *args, **kwargs):
        self.database = database

    def create_event(self, event: EventData):
        return self.database.create_event(**asdict(event))

    def get_all_user_events(self, user_id):
        return [EventData(*i) for i in self.database.get_all_user_events(user_id)]

    def get_all_events(self):
        return [EventData(*i) for i in self.database.get_all_events()]

    def delete_event(self, _id):
        self.database.delete_event(_id)


