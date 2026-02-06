from django.contrib.auth.models import User
from django.db import models


def avatar_directory_path(instance: "Profile", avatar_name: str) -> str:
    """Генерация пути для сохранения аватара"""
    directory_path = "myauth/profile_{pk}/avatar/{filename}".format(pk=instance.pk, filename=avatar_name)
    return directory_path

class Profile(models.Model):
    """Модель пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to=avatar_directory_path)
