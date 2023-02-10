from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone


# Create your models here.

class CustomManager(BaseUserManager):
    def create_user(self, email, password):
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(

            email=self.normalize_email(email),
            # username = username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email", unique=True, max_length=60,blank=True, null=True)
    username = None
    date_joined = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class TODO(models.Model):
    status_choices = [
        ('C', 'COMPLETED'),
        ('P', 'PENDING'),
    ]
    priority_choices = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),

    ]

    tasks = models.CharField(max_length=50,null=True,blank=True)
    status = models.CharField(max_length=10, choices=status_choices)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=2, choices=priority_choices)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tasks


class UserOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.SmallIntegerField()

    def __str__(self):
        return str(self.user)
