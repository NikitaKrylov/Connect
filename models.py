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


@dataclass
class EventData:
    id: int
    time_start: str
    time_end: str
    description: str


@dataclass
class ImageData:
    id: int
    path: str
