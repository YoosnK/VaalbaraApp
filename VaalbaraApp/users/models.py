from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    photo = models.ImageField(
        upload_to="user_photos",
        default="user_photos/default_avatar.png",
        null=True,
        blank=True,
    )
    age = models.PositiveIntegerField(null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"