from django.urls import path
from .views import StoreListView, StoreLikeView, LikedStoreListView

urlpatterns = [
    path('distance_order/', StoreListView.as_view()),  # 거리순 가맹점 리스트 반환
    path('like/<int:pk>/', StoreLikeView.as_view(), name='like_post'),  # 좋아요
    path('liked_list/', LikedStoreListView.as_view()),  # 좋아요 리스트 반환
]