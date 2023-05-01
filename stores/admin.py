from django.contrib import admin
from .models import StoreDaegu, Review


class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'store_name', 'store_address', 'category', 'likes_count', 'rating_mean')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_name', 'author', 'short_content', 'rating', 'published_data', 'modified_date', 'reported_num')

    def store_name(self, obj):
        return obj.store.store_name

    def short_content(self, obj):
        return obj.content[:15] + '…' if len(obj.content) > 10 else obj.content


admin.site.register(StoreDaegu, StoreAdmin)
admin.site.register(Review, ReviewAdmin)