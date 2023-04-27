from django.urls import path
from .views import StoreListView, StoreLikeView

urlpatterns = [
    path('distance_order/', StoreListView.as_view()),
    path('like/<int:pk>/', StoreLikeView.as_view(), name='like_post')
]