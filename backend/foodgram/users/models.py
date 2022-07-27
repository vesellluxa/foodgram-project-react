from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodUserManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, username):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email,
            password,
            first_name,
            last_name,
            username):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class FoodUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'

    """Кастомная модель User."""
    ROLES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
    ]

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False)
    first_name = models.CharField(
        max_length=150,
        unique=False,
        blank=False,
        null=False)
    last_name = models.CharField(
        max_length=150,
        unique=False,
        blank=False,
        null=False)
    password = models.CharField(max_length=150)
    role = models.CharField(max_length=100, choices=ROLES, default=USER)
    is_staff = models.BooleanField(default=False)

    objects = FoodUserManager()

    def is_following(self, instance):
        return Follow.objects.filter(user=self, following=instance).exists()


class Follow(models.Model):
    user = models.ForeignKey(
        FoodUser,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        FoodUser,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_followers'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='not_sub'
            )
        ]
