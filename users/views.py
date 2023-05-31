from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, \
    PasswordChangeSerializer, UsernameFindSerializer
from .models import Profile, MyUser, Withdrawal
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import requests


# 소셜 로그인
BASE_URL = 'http://127.0.0.1:8000/api/v1/accounts/rest-auth/'
KAKAO_CALLBACK_URI = BASE_URL + 'kakao/callback/'
NAVER_CALLBACK_URI = BASE_URL + 'naver/callback/'


class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callbakc_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs).data
        profile = Profile.objects.get(user=self.request.user)
        social_user = profile.user
        if social_user.location == "":
            social_user.location = "거주지_선택"
            profile.location = "거주지_선택"
            if MyUser.objects.filter(nickname=request.data.get('nickname')).exists():
                social_user.nickname = f"Kakao_{request.data.get('email').split('@')[0]}"
                profile.nickname = f"Kakao_{request.data.get('email').split('@')[0]}"
            else:
                social_user.nickname = request.data.get('nickname')
                profile.nickname = request.data.get('nickname')
            social_user.save()
            profile.save()
        additional_data = {
            "user_id": profile.pk,
            "location": social_user.location
        }
        response.update(additional_data)
        return Response(response, status=status.HTTP_200_OK)


class NaverLogin(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs).data
        profile = Profile.objects.get(user=self.request.user)
        social_user = profile.user
        
        # 네이버에서 사용자 정보 갖고 오기
        user_info_request = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {request.data.get('access_token')}"},
        )

        # 사용자 정보를 가지고 오는 요청이 잘못된 경우
        if user_info_request.status_code != 200:
            return Response({"message": "정보를 가져오는데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
        user_info = user_info_request.json().get("response")
        email = user_info["email"]
        nickname = user_info["nickname"]

        if social_user.location == "":
            social_user.location = "거주지_선택"
            profile.location = "거주지_선택"
            if MyUser.objects.filter(nickname=nickname).exists():
                social_user.nickname = f"Naver_{email.split('@')[0]}"
                profile.nickname = f"Naver_{email.split('@')[0]}"
            else:
                social_user.nickname = nickname
                profile.nickname = nickname
            social_user.save()
            profile.save()

        additional_data = {
            "user_id": profile.pk,
            "location": social_user.location
        }
        response.update(additional_data)
        return Response(response, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data
        return Response({"user_id": user.pk, "token": token.key}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        password = request.data.get('password')
        if not user.check_password(password):
            return Response({'error': '비밀번호가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal = Withdrawal(user=user, location=user.location, location2=user.location2, reason=request.data.get('reason'))
        withdrawal.save()
        self.perform_destroy(instance)
        user.delete()
        return Response({'detail': '이용해주셔서 감사했습니다. 탈퇴처리가 되었습니다.'}, status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': '비밀번호가 성공적으로 변경되었습니다.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsernameFindView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UsernameFindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '입력하신 이메일로 아이디를 보냈습니다.'}, status=status.HTTP_200_OK)


class CustomPasswordResetView(APIView):  # 이메일 입력받아서 비밀번호 초기화 메일 전송
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request):
        email = request.data.get('email')
        username = request.data.get('username')
        user_queryset = MyUser.objects.filter(email=email, username=username)

        if user_queryset.exists():
            form = PasswordResetForm({'email': email})
            if form.is_valid():
                try:
                    form.save(
                        email_template_name='registration/password_reset_email.html',
                        domain_override=request.get_host(),
                        # subject_template_name='users/password_reset.txt'
                    )
                except ValidationError:
                    return Response({'message': '비밀번호 초기화 이메일을 전송하지 못했습니다.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': '비밀번호 초기화 이메일을 전송했습니다.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': '입력값이 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': '해당하는 사용자가 존재하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class LeftMoneyCheckView(APIView):
    def get_object(self, pk):
        try:
            return Profile.objects.get(user__pk=pk)
        except Profile.DoesNotExist:
            raise Response({'message': '회원 정보가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        profile = self.get_object(pk)
        url_mapping = {
            "대구광역시": "https://www.shinhancard.com/mob/MOBFM064N/MOBFM064R01.shc",
            "경상북도": "http://gb.nhdream.co.kr/Login/PointCheck.jsp",
        }
        url = url_mapping.get(profile.location)
        if url:
            return Response({'url': url}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '해당 지역의 잔액조회 사이트가 없습니다. 거주지 정보를 확인해주세요'}, status=status.HTTP_404_NOT_FOUND)
