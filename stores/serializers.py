from rest_framework import serializers
from .models import StoreDaegu
import math


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