import os

from typing import Optional, Tuple, List

from telethon import TelegramClient
from telethon.sessions import StringSession

from accounts.models import Account
from tg_sessions.models import TgSession


api_id: str = os.getenv('TELEGRAM_API_ID')
api_hash: str = os.getenv('TELEGRAM_API_HASH')


async def get_telegram_client(phone: str):
    """
    Возвращает TelegramClient и соответствующего пользователя по номеру телефона.

    :param phone: Номер телефона пользователя.
    :type phone: str
    :return: Кортеж, содержащий TelegramClient и объект Account (или None, если пользователь не найден).
    :rtype: Tuple[TelegramClient, Optional[Account]]
    """
    try:
        user: Account = Account.objects.get(phone=phone)
        session_string: str = user.tgsession.tg_session_string if user.tgsession.tg_session_string else ''
        client: TelegramClient = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.connect()
        return client, user
    except Account.DoesNotExist:
        client: TelegramClient = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        return client, None


async def generate_qr_code(phone: str) -> str:
    """
    Генерирует QR-код для авторизации пользователя по номеру телефона.

    :param phone: Номер телефона пользователя.
    :type phone: str
    :return: URL для QR-кода.
    :rtype: str
    """
    client, user = await get_telegram_client(phone)
    qr_login = await client.qr_login()

    if user:
        tg_session = user.tgsession
    else:
        tg_session = TgSession.objects.create(user=user, tg_session_string="")

    session_string = StringSession.save(tg_session.tg_session_string)
    tg_session.tg_session_string = session_string
    tg_session.save()

    return qr_login.url


async def check_login(phone: str) -> bool:
    """
    Проверяет, авторизован ли пользователь.

    :param phone: Номер телефона пользователя.
    :type phone: str
    :return: True, если пользователь авторизован, иначе False.
    :rtype: bool
    """
    client, _ = await get_telegram_client(phone)
    is_authorized: bool = await client.is_user_authorized()
    return is_authorized


async def send_message(phone: str, username: str, message: str) -> None:
    """
    Отправляет сообщение пользователю.

    :param phone: Номер телефона отправителя.
    :type phone: str
    :param username: Имя пользователя получателя.
    :type username: str
    :param message: Текст сообщения.
    :type message: str
    """
    client, _ = await get_telegram_client(phone)
    await client.send_message(username, message)


async def get_messages(phone: str, username: str, limit: int = 50) -> List[dict]:
    """
    Получает последние сообщения из чата.

    :param phone: Номер телефона пользователя.
    :type phone: str
    :param username: Имя пользователя чата.
    :type username: str
    :param limit: Количество сообщений для получения (по умолчанию 50).
    :type limit: int
    :return: Список сообщений.
    :rtype: List[dict]
    """
    client, _ = await get_telegram_client(phone)
    messages = await client.get_messages(username, limit=limit)
    result: List[dict] = [
        {
            'username': message.sender.username if message.sender else None,
            'is_self': message.out,
            'message_text': message.message
        } for message in messages
    ]
    return result
