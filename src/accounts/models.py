import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from app.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """Custom User model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars", blank=True, null=True, verbose_name="Аватар"
    )
    bio = models.TextField(blank=True, verbose_name="О себе")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
