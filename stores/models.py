from django.db import models
from users.models import Profile, MyUser
from django.utils import timezone


class StoreDaegu(models.Model):
    store_id = models.IntegerField()
    store_name = models.CharField(max_length=30)
    store_address = models.CharField(max_length=30)
    latitude = models.FloatField()  # 위도
    longitude = models.FloatField()  # 경도
    category = models.CharField(max_length=10)
    menu = models.CharField(max_length=100)
    likes = models.ManyToManyField(MyUser, related_name='like_posts', blank=True, null=True)
    rating_mean = models.FloatField(null=True)  # 평균 평점

    class Meta:
        ordering = ['store_id']

# class Review(models.Model):
#     review_id = models.IntegerField
#     author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
#     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     store = models.ForeignKey(StoreDaegu, on_delete=models.CASCADE)
#     content = models.TextField()
#     rating = models.IntegerField()
#     published_data = models.DateTimeField(default=timezone.now)
#     reported_num = models.IntegerField()
