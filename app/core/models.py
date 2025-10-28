"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    """Managers for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) #LOGIN WITH DJANGO ADMIN

    objects = UserManager()

    USERNAME_FIELD = 'email'