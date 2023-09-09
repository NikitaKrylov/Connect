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
    image: str = None


@dataclass
class EventData:
    id: int
    author_id: int
    location: str
    time_start: str
    description: str
    invite_link: str
    time_end: str = None
    image: str = None

