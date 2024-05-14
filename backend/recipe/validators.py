import re

from rest_framework.exceptions import ValidationError
from PIL import ImageColor

from backend.settings import USER_URL_PATH_NAME


def validate_amount(number):
    if number <= 0:
        raise ValidationError('Вес должен быть больше 0.')


def validate_hex_color(color):
    try:
        ImageColor.getcolor(color, 'RGB')
    except ValueError:
        raise ValidationError(
            f'цвет "{color}" не соответствует HEX кодировке.'
        )


def validate_username(username):
    if username == USER_URL_PATH_NAME:
        raise ValidationError(
            f'Неверное имя пользователя: {username}.'
        )
    check_symbols = re.sub(r'[\w.@+-]', '', username)
    if check_symbols:
        bad_symbols = ''.join(set(check_symbols))
        raise ValidationError(
            'В Имени пользователя использованы запрещённые символы: '
            f'{bad_symbols} '
            'Введите корректное имя пользователя. '
            'username может содержать только латинские буквы, '
            'символы @/./+/-/_ и цифры.'
        )
    return username
