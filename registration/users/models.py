from django.contrib.auth.models import AbstractUser

from django.db import models
import random
import string


class CustomUser(AbstractUser):
    """Абстарктная модель пользователя"""
    phone = models.CharField(max_length=15, unique=True)

    # Убираем ненужные поля
    username = None
    groups = None
    user_permissions = None

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []


class Profile(models.Model):
    """Модель пользователя"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    invite_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    activated_invite = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )

    @staticmethod
    def generate_invite_code():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(6))
