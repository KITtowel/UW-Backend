from django.urls import path
from .views import RegisterView, LoginView, ProfileView, PasswordChangeView, UsernameFindView, CustomPasswordResetView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('register/', RegisterView.as_view()),  # 회원가입
    path('login/', LoginView.as_view()),  # 로그인
    path('profile/<int:pk>/', ProfileView.as_view()),  # 프로필 수정 및 가져오기 및 탈퇴
    path('password_change/', PasswordChangeView.as_view()),  # 비밀번호 변경
    path('username_find/', UsernameFindView.as_view()),  # 아이디 찾기
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),  # 비밀번호 초기화
    path('password_reset/', CustomPasswordResetView.as_view(), name="password_reset"),  # 비밀번호 초기화
    # path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),  # 비밀번호 초기화 이메일 전송 완료
    path('password_reset_confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),  # 비밀번호 초기화 url
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),  # 비밀번호 변경 완료
]