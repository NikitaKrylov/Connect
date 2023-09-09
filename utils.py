from typing import List
from aiogram.types.photo_size import PhotoSize

from database import Database
from models import UserData


async def download_image(path: str, photo: PhotoSize):
    _path = f'{path}{photo.file_unique_id}.jpg'
    await photo.download(_path)
    return _path




