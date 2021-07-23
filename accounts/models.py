import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

LEVEL = (
    ("100L", "100L"),
    ("200L", "200L"),
    ("300L", "300L"),
    ("400L", "400L"),
)

ALIAS = (("Mr.", "Mr."), ("Mrs", "Mrs"), ("Dr.", "Dr."), ("Prof.", "Prof."))

GENDER = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Prefer not to mention", "Prefer not to mention"),
)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    alias = models.CharField(choices=ALIAS, max_length=5, null=True, blank=True)
    level = models.CharField(choices=LEVEL, max_length=11, null=True, blank=True)
    gender = models.CharField(choices=GENDER, max_length=22)
    has_logged_in = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
