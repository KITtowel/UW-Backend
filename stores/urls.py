from django.urls import path
from .views import StoreListView, StoreLikeView, LikedStoreListView, LikedCountStoreListView

urlpatterns = [
    path('distance_order/', StoreListView.as_view()),  # 거리순 가맹점 리스트 반환
    path('like/<int:pk>/', StoreLikeView.as_view(), name='like_post'),  # 좋아요
    path('liked_list/', LikedStoreListView.as_view()),  # 사용자의 좋아요 리스트 반환
    path('like_order/', LikedCountStoreListView.as_view())  # 가맹점의 좋아요 개수 순으로 리스트 반환
]