from dataclasses import dataclass


@dataclass
class UserProfile:
    name: str
    age: int
    group: str
    description: str

@dataclass
class UserData:
    id: int
    name: str
    age: int
    group: str
    description: str
    isActive: int
@dataclass
class EventData:
    id: int
    time_start : str
    time_end : str
    description : str
@dataclass
class ImageData:
    id: int
    path : str
