from django.contrib import admin
from .models import StoreDaegu, Review, Report


class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'store_name', 'store_address', 'category', 'likes_count', 'rating_mean')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_name', 'store_id', 'author', 'short_content', 'rating', 'published_data', 'modified_date', 'reported_num')

    def store_id(self, obj):
        return obj.store.store_id

    def store_name(self, obj):
        return obj.store.store_name

    def short_content(self, obj):
        return obj.content[:12] + '…' if len(obj.content) > 10 else obj.content


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_id', 'store_name', 'review_id', 'review_author', 'reason', 'reported_num')

    def store_name(self, obj):
        return obj.store.store_name

    def store_id(self, obj):
        return obj.store.store_id

    def review_id(self, obj):
        return obj.review.id

    def review_author(self, obj):
        return obj.review.author.username

    def reported_num(self, obj):
        return obj.review.reported_num


admin.site.register(StoreDaegu, StoreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Report, ReportAdmin)