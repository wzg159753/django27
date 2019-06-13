from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager
# Create your models here.


class UserManager(_UserManager):

    def create_superuser(self, username, password, email=None, **extra_fields):
        super(UserManager, self).create_superuser(username=username, password=password, email=email, **extra_fields)


class Users(AbstractUser):

    objects = UserManager()

    REQUIRED_FIELDS = ['mobile']

    # 自定义mobile字段
    mobile = models.CharField(verbose_name='电话号码', max_length=11, unique=True, help_text='手机号',
                              error_messages={'unique': '电话号码已存在'})

    email_active = models.BooleanField(default=False, verbose_name='验证邮箱状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username