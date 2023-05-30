from django.urls import path
from .views import StoreListView, StoreLikeView, LikedStoreListView, StoreDetailView, MapMarkView, \
    ReviewCreateView, ReviewView, UserReviewListView, ReviewReportView, CategoryListView, SearchListView, \
    CategoryMapMarkView, SearchMapMarkView

urlpatterns = [
    path('distance_order/', StoreListView.as_view(), name='distance_list'),  # 거리순 가맹점 리스트 반환
    path('like_order/', StoreListView.as_view(), name='like_list'),  # 가맹점의 좋아요 개수 순으로 리스트 반환
    path('rating_order/', StoreListView.as_view(), name='rating_list'),  # 평균 평점이 높은 순으로 리스트 반환
    path('like/<int:pk>/', StoreLikeView.as_view(), name='like_post'),  # 좋아요
    path('liked_list/', LikedStoreListView.as_view()),  # 사용자의 좋아요 리스트 반환
    path('detail/<int:store_id>/', StoreDetailView.as_view(), name='store_detail'),  # 가맹점 상세보기
    path('detail/<int:store_id>/reviews/', ReviewCreateView.as_view(), name='create_review'),  # 가맹점 후기글 작성
    path('reviews/<int:pk>/', ReviewView.as_view(), name='review_detail'),  # 가맹점 후기글 조회, 수정, 삭제
    path('reviewed_list/', UserReviewListView.as_view()),  # 사용자가 작성한 가맹점 후기글 리스트 반환
    path('reviews/<int:pk>/report/', ReviewReportView.as_view(), name='review_report'),  # 가맹점 후기글 신고
    path('category_distance_order/', CategoryListView.as_view(), name='category_distance'),  # 카테고리별 가맹점 리스트 반환 (거리순)
    path('category_like_order/', CategoryListView.as_view(), name='category_like'),  # 카테고리별 가맹점 리스트 반환 (좋아요순)
    path('category_rating_order/', CategoryListView.as_view(), name='category_rating'),  # 카테고리별 가맹점 리스트 반환 (평점순)
    path('search_distance_order/', SearchListView.as_view(), name='search_distance'),  # 검색어 기반 가맹점 리스트 반환 (거리순)
    path('search_like_order/', SearchListView.as_view(), name='search_like'),  # 검색어 기반 리스트 반환 (좋아요순)
    path('search_rating_order/', SearchListView.as_view(), name='search_rating'),  # 검색어 기반 가맹점 리스트 반환 (평점순)
    path('map_mark/', MapMarkView.as_view()),  # 지도 마커용 가맹점 리스트 반환
    path('category_map_mark/', CategoryMapMarkView.as_view()),  # 지도 마커용 카테고리별 가맹점 리스트 반환
    path('search_map_mark/', SearchMapMarkView.as_view()),  # 지도 마커용 검색어별 가맹점 리스트 반환
]