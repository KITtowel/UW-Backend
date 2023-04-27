from django.contrib import admin
from .models import StoreDaegu


class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'store_name', 'store_address', 'category', 'likes_count', 'rating_mean')

    def likes_count(self, obj):
        return obj.likes.count()


admin.site.register(StoreDaegu, StoreAdmin)