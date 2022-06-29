from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.shortcuts import reverse
from datetime import date
import uuid
from django_softdelete.models import SoftDeleteModel, SoftDeleteManager


class Country(models.Model):
    alpha_3 = models.TextField(db_column='CRY_COD', primary_key=True, max_length=3)
    name = models.TextField(db_column='CRY_NAM', max_length='255')

    def __str__(self):
        return self.name


# Create your models here.
class UserManager(SoftDeleteManager, BaseUserManager):
    def create_user(self, username, description, password=None, user_id=None, country_code=None, is_superuser=False):
        if not username:
            raise ValueError("User must have a email")
        if not password:
            raise ValueError("User must have a password")
        if not description:
            raise ValueError("User must have a description")

        user = self.model(
            username=self.normalize_email(username)
        )
        user.set_password(password)  # change password to hash
        user.description = description
        user.country_code = country_code
        user.user_id = user_id
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, username, description, country_code=None, user_id=None, password=None):
        if user_id is None:
            user_id = uuid.uuid4()
        user = self.create_user(
            username=username,
            description=description,
            country_code=country_code,
            password=password,
            user_id=user_id,
            is_superuser=True,
        )
        return user

    def get_by_natural_key(self, username):
        return User.objects.get(username=username)


class User(SoftDeleteModel, AbstractBaseUser):
    username = models.EmailField(verbose_name='User email', max_length=255, primary_key=True, unique=True, db_column='USR_EML')
    user_id = models.UUIDField(default=uuid.uuid4, db_column='USR_COD')
    description = models.CharField(max_length=255, db_column='USR_NAM', blank=True)
    country_code = models.ForeignKey(Country, db_column='CRY_COD', blank=True, null=True, on_delete=models.CASCADE)
    date_joined = models.DateField(default=date.today, db_column='ENT_DAT')
    is_superuser = models.BooleanField(default=False, db_column='ADM_FLG')
    absence_limit = models.IntegerField(default=0, db_column='ABS_LMT')

    is_deleted = models.BooleanField(default=False, db_column='T_REC_DLT_FLG')
    created_at = models.DateTimeField(auto_now_add=True, db_column='T_REC_INS_TST')
    updated_at = models.DateTimeField(auto_now=True, db_column='T_REC_UPD_TST')
    deleted_at = models.DateTimeField(db_column='T_REC_SRC_TST', null=True)

    REQUIRED_FIELDS = ['description']
    USERNAME_FIELD = 'username'
    objects = UserManager()

    def get_absolute_url(self):
        return reverse(
            'accounts:profile', kwargs={'username': self.username})

    def __str__(self):
        deleted = '<deleted> ' if self.is_deleted else ''
        return f'{deleted}{self.username}'

    @property
    def is_active(self):
        return not self.is_deleted

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_admin(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    class Meta:
        db_table = 'R_USR'