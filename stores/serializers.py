from rest_framework import serializers
from .models import StoreDaegu, Review
from users.models import MyUser
from haversine import haversine
from datetime import datetime
from django.core.validators import MinLengthValidator, MinValueValidator
from users.serializers import ProfileSerializer


class MapMarkSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = StoreDaegu
        fields = ('store_id', 'category', 'latitude', 'longitude', 'distance')

    def get_distance(self, obj):
        if 'user_latitude' in self.context and 'user_longitude' in self.context:
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


class StoreListSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = StoreDaegu
        fields = ('store_id', 'store_name', 'store_address', 'category', 'latitude', 'longitude',
                  'rating_mean', 'likes_count', 'reviews_count', 'distance')

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

    def get_reviews_count(self, obj):
        return obj.reviews.count()


class StoreDetailSerializer(serializers.ModelSerializer):
    liked_by_user = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
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

    def get_reviews(self, obj):
        full_data = []
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.reviews.filter(author=request.user.id).exists():
                first_batch = obj.reviews.filter(author=request.user.id)
                first_batch_serializer = ReviewSerializer(first_batch, many=True,
                                                          context={'request': self.context.get('request')}).data
                remain_batch = obj.reviews.exclude(author=request.user.id)
                remain_batch_serializer = ReviewSerializer(remain_batch, many=True,
                                                           context={'request': self.context.get('request')}).data
                first_data = sorted(first_batch_serializer,
                                    key=lambda x: datetime.strptime(x['published_data'].strftime('%Y-%m-%d %H:%M:%S'),
                                                                    '%Y-%m-%d %H:%M:%S'), reverse=True)
                remain_data = sorted(remain_batch_serializer,
                                     key=lambda x: datetime.strptime(x['published_data'].strftime('%Y-%m-%d %H:%M:%S'),
                                                                     '%Y-%m-%d %H:%M:%S'), reverse=True)
                full_data = first_data + remain_data
            else:
                serializer = ReviewSerializer(obj.reviews, many=True,
                                              context={'request': self.context.get('request')}).data
                full_data = sorted(serializer,
                                   key=lambda x: datetime.strptime(x['published_data'].strftime('%Y-%m-%d %H:%M:%S'),
                                                                   '%Y-%m-%d %H:%M:%S'), reverse=True)
        else:
            serializer = ReviewSerializer(obj.reviews, many=True, context={'request': self.context.get('request')}).data
            full_data = sorted(serializer,
                               key=lambda x: datetime.strptime(x['published_data'].strftime('%Y-%m-%d %H:%M:%S'),
                                                               '%Y-%m-%d %H:%M:%S'), reverse=True)
        return full_data


class ReviewListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.store_name')
    store_address = serializers.CharField(source='store.store_address')
    category = serializers.CharField(source='store.category')

    class Meta:
        model = Review
        fields = ('id', 'store_name', 'store_address', 'category', 'content', 'rating', 'published_data',
                  'modified_date', 'reported_num')


class LikedListSerializer(serializers.ModelSerializer):
    liked_id = serializers.SerializerMethodField()

    class Meta:
        model = StoreDaegu
        fields = ('store_id', 'store_name', 'store_address', 'category', 'rating_mean', 'likes_count', 'liked_id')

    def get_liked_id(self, obj):
        user = MyUser.objects.get(username=self.context.get('user'))
        likes_instance = obj.likes.through.objects.filter(storedaegu_id=obj.id, myuser_id=user.id).first()
        return likes_instance.id
