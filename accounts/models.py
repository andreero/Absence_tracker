from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.shortcuts import reverse
from datetime import date
import uuid


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, description, password=None, user_id=None, is_superuser=False):
        if not username:
            raise ValueError("User must have an username")
        if not password:
            raise ValueError("User must have a password")
        if not description:
            raise ValueError("User must have a description")

        user = self.model(
            username=self.normalize_email(username)
        )
        user.set_password(password)  # change password to hash
        user.description = description
        user.user_id = user_id
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, username, description, user_id=None, password=None):
        user = self.create_user(
            username=username,
            description=description,
            password=password,
            user_id=user_id,
            is_superuser=True,
        )
        return user


class User(AbstractUser):
    # user_id = models.UUIDField(default=uuid.uuid4, db_column='USR_COD')
    username = models.EmailField(primary_key=True, unique=True, max_length=255, db_column='USR_EML')
    description = models.CharField(max_length=255, db_column='USR_NAM', blank=True)
    # country_code = models.CharField(max_length=3, db_column='CRY_COD', blank=True)
    date_joined = models.DateField(default=date.today, db_column='ENT_DAT')
    is_superuser = models.BooleanField(default=False, db_column='ADM_FLG')
    absence_limit = models.IntegerField(default=0, db_column='ABS_LMT')

    is_deleted = models.BooleanField(default=False, db_column='T_REC_DLT_FLG')
    created_at = models.DateTimeField(auto_now_add=True, db_column='T_REC_INS_TST')
    updated_at = models.DateTimeField(auto_now=True, db_column='T_REC_UPD_TST')
    deleted_at = models.DateTimeField(db_column='T_REC_SRC_TST', null=True)

    REQUIRED_FIELDS = []
    objects = UserManager()

    # prevent default columns from being created
    first_name = None
    last_name = None
    email = None

    def get_absolute_url(self):
        return reverse(
            'accounts:profile', kwargs={'username': self.username})

    def __str__(self):
        return self.username

    @property
    def is_active(self):
        return not self.is_deleted

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_admin(self):
        return self.is_superuser

    class Meta:
        db_table = 'R_USR'

