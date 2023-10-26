import string
import os
from random import choice
from werkzeug.utils import secure_filename
from http import HTTPStatus

from . import UPLOAD_FOLDER
from app.model import User
from app.error_handlers import InvalidAPIUsage


def get_unique_filename():
    str_ = string.ascii_letters
    for i in range(1, 10):
        str_ += str(i)
    new_str = ''
    while len(new_str) <= 5:
        new_str += choice(str_)
    return new_str


def get_file_name(filename_hash, file):
    file_format = f'.{file.filename.rsplit(".", 1)[1].lower()}'
    file_name = secure_filename(filename_hash)
    file_name = file_name + file_format
    return file_name


def check_user_auth(request):
    username = request.authorization["username"]
    password = request.authorization["password"]
    db_user = User.query.filter_by(
        username=username,
        password=password
        ).first()
    if not db_user:
        raise InvalidAPIUsage(
            'Пользователь не авторизован',
            HTTPStatus.UNAUTHORIZED
            )
    return db_user


def check_user_is_author(db_user, hash_file_name):
    db_user_file = db_user.user_files
    if hash_file_name not in db_user_file:
        raise InvalidAPIUsage(
            'Вы не являетесь автором файла',
            HTTPStatus.BAD_REQUEST
            )
    return


def find_file(hash_file_name):
    file_path = UPLOAD_FOLDER + hash_file_name[:2] + '/'
    try:
        file_list = os.listdir(file_path)
    except Exception:
        raise InvalidAPIUsage(
            'Директория с файлом не найдена',
            HTTPStatus.NOT_FOUND
        )
    for file_name in file_list:
        if file_name.split('.')[0] == hash_file_name:
            file_path += file_name
            break
        if file_name.split('.')[0] not in file_list:
            raise InvalidAPIUsage(
                'Файл не найден',
                HTTPStatus.NOT_FOUND
            )
    return file_path, file_list
