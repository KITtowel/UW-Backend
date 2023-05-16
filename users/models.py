from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    nickname = models.CharField(max_length=20, blank=False, null=False, unique=True)
    location = models.CharField(max_length=20, blank=False, null=False)
    location2 = models.CharField(max_length=20, blank=True, default='')


class Profile(models.Model):  # 프로필 모델 MyUser 모델과 일대일 관계
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=20, blank=False, null=False, unique=True)
    location = models.CharField(max_length=20, blank=False, null=False)
    location2 = models.CharField(max_length=20, blank=True, default='')
    image = models.ImageField(upload_to="profile/", default='default.png')


class Withdrawal(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=20, blank=False, null=False)
    location2 = models.CharField(max_length=20, blank=True, default='')
    reason = models.CharField(max_length=100, blank=False, null=False)


@receiver(post_save, sender=MyUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, nickname=instance.nickname, location=instance.location,
                                         location2=instance.location2)
        instance.profile = profile
        instance.profile.save()
