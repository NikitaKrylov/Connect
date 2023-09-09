from dataclasses import dataclass


@dataclass
class UserProfile:
    name: str
    age: int
    group: str
    description: str
    image_path: str

