from rest_framework import serializers
from .models import StoreDaegu, Review
from haversine import haversine
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
            # 일직선상 거리 공식 -> 지구는 둥글기 때문에 정확하지 않음
            # user_latitude = self.context['user_latitude']
            # user_longitude = self.context['user_longitude']
            # distance = math.sqrt((obj.latitude - user_latitude) ** 2 + (obj.longitude - user_longitude) ** 2)
        
            # 하버사인(haversine)공식: 둥근 지구 표면에 있는 두 지점 사이의 직선 거리 구하는 공식
            user_point = (self.context['user_latitude'], self.context['user_longitude'])  # 사용자 현재 위치 위도, 경도
            store_point = (obj.latitude, obj.longitude)
            distance = haversine(user_point, store_point, unit='mi')  # 단위는 MILES
            return distance
        else:
            return None


class ReviewCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=200, validators=[MinLengthValidator(10)])
    rating = serializers.FloatField(validators=[MinValueValidator(1.0)])

    class Meta:
        model = Review
        fields = ('store_id', 'content', 'rating')


class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    published_data = serializers.ReadOnlyField()
    reported_num = serializers.ReadOnlyField()

    class Meta:
        model = Review
        fields = ('id', 'author', 'profile', 'store', 'content', 'rating', 'published_data',
                  'modified_date', 'reported_num')


class StoreDetailSerializer(serializers.ModelSerializer):
    liked_by_user = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = StoreDaegu
        fields = ('store_id', 'store_name', 'store_address', 'category', 'latitude', 'longitude',
                  'rating_mean', 'liked_by_user', 'likes_count', 'menu', 'reviews_count', 'reviews')

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.likes.filter(username=request.user.username).exists():
                return True
        return False

    def get_reviews_count(self, obj):
        return obj.reviews.count()


class ReviewListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.store_name')
    store_address = serializers.CharField(source='store.store_address')
    category = serializers.CharField(source='store.category')

    class Meta:
        model = Review
        fields = ('id', 'store_name', 'store_address', 'category', 'content', 'rating', 'published_data',
                  'modified_date', 'reported_num')