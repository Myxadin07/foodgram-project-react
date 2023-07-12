from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):
    '''Модель пользователей'''

    REQUIRED_FIELDS = ('first_name', 'last_name', 'username',)
    USERNAME_FIELD = 'email'

    email = models.EmailField(max_length=254, unique=True, blank=False)
    confirmation_code = models.CharField(
        max_length=255, blank=True, null=True
    )
    subscriptions = models.ManyToManyField(to='self', related_name='followers')

    @property
    def is_admin(self):
        return self.role == self.is_superuser

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
