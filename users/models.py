from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    location = models.CharField(max_length=100, blank=False, null=False)


class Profile(models.Model):  # 프로필 모델 user 모델과 일대일 관계, user 모델은 따로 만들지 않아도 장고에 기본으로 사용 가능
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=128)
    location = models.CharField(max_length=100, blank=False, null=False)
    image = models.ImageField(upload_to="profile/", default='default.png')


@receiver(post_save, sender=MyUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.location = instance.location
        instance.profile.save()

