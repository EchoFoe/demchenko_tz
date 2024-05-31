from django.db import models

from demchenko_tz.bases import DateTimeBaseModel
from accounts.models import Account


class TgSession(DateTimeBaseModel):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, verbose_name='Пользователь')
    tg_session_string = models.CharField(max_length=255, verbose_name='Строка сессии')

    class Meta:
        verbose_name = 'Телеграм сессия'
        verbose_name_plural = 'Телеграм сессии'

    def __str__(self):
        return f'Сессия для пользователя {self.user.username}'
