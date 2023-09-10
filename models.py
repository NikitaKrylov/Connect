from dataclasses import dataclass


@dataclass
class UserProfile:
    name: str
    age: int
    team: str
    description: str
    image: str


@dataclass
class UserData:
    id: int
    name: str
    age: int
    team: str
    description: str
    isActive: int
    image: str
    lang: str


@dataclass
class EventData:
    id: int
    author_id: int
    location: str
    time: str
    description: str
    invite_link: str
    image: str = None

