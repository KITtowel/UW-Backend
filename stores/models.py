from django.db import models
from users.models import Profile, MyUser
from django.utils import timezone
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.validators import MaxValueValidator


class StoreDaegu(models.Model):
    store_id = models.IntegerField()
    store_name = models.CharField(max_length=30)
    store_address = models.CharField(max_length=30)
    latitude = models.FloatField()  # 위도
    longitude = models.FloatField()  # 경도
    category = models.CharField(max_length=10)
    menu = models.CharField(max_length=100)
    likes = models.ManyToManyField(MyUser, related_name='like_posts', blank=True)
    rating_mean = models.FloatField(default=0)  # 평균 평점
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['store_id']


@receiver(m2m_changed, sender=StoreDaegu.likes.through)
def update_likes_count(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove':
        instance.likes_count = instance.likes.count()
        instance.save()


class Review(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    store = models.ForeignKey(StoreDaegu, on_delete=models.CASCADE, related_name='reviews')
    content = models.CharField(max_length=200)
    rating = models.FloatField(validators=[MaxValueValidator(5.0)])
    published_data = models.DateTimeField(default=timezone.now)
    reported_num = models.IntegerField(default=0)
    modified_date = models.DateTimeField(auto_now=True)
