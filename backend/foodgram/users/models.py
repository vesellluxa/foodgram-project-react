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
            username):
        user = self.model(
            email=self.normalize_email(email),
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

    email = models.EmailField(verbose_name='email',
                              max_length=254,
                              unique=True)
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=150)
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=150)
    password = models.CharField(verbose_name='Пароль',
                                max_length=150)
    role = models.CharField(verbose_name='Роль',
                            max_length=100, choices=ROLES, default=USER)
    is_staff = models.BooleanField(verbose_name='Сотрудник',
                                   default=False)

    objects = FoodUserManager()

    def followings(self):
        return Follow.objects.filter(
            user=self).values_list('following', flat=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=FoodUser,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        verbose_name='Подписан',
        to=FoodUser,
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

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
