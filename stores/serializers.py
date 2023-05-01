from rest_framework import serializers
from .models import StoreDaegu, Review
import math
from django.core.validators import MinLengthValidator, MinValueValidator
from users.serializers import ProfileSerializer


class StoreListSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = StoreDaegu
        fields = ('store_id', 'store_name', 'store_address', 'category', 'latitude', 'longitude',
                  'rating_mean', 'likes_count', 'distance')

    def get_distance(self, obj):
        if 'user_latitude' in self.context and 'user_longitude' in self.context:
            user_latitude = self.context['user_latitude']
            user_longitude = self.context['user_longitude']
            distance = math.sqrt((obj.latitude - user_latitude) ** 2 + (obj.longitude - user_longitude) ** 2)
            return distance
        else:
            return None


class ReviewCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=200, validators=[MinLengthValidator(10)])
    rating = serializers.FloatField(validators=[MinValueValidator(1.0)])

    class Meta:
        model = Review
        fields = ('store_id', 'content', 'rating')


class StoreDetailSerializer(serializers.ModelSerializer):
    liked_by_user = serializers.SerializerMethodField()
    # reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = StoreDaegu
        fields = ('store_id', 'store_name', 'store_address', 'category', 'latitude', 'longitude',
                  'rating_mean', 'liked_by_user', 'likes_count', 'menu')

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.likes.filter(username=request.user.username).exists():
                return True
        return False