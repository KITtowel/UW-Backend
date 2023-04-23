from django.urls import path
from .views import StoreListView

urlpatterns = [
    path('distance_order/', StoreListView.as_view()),
]