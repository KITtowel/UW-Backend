from json import JSONDecodeError
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
from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.providers.naver import views as naver_views
from allauth.socialaccount.providers.kakao import views as kakao_views
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import requests

main_domain = settings.MAIN_DOMAIN


class NaverLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        client_id = settings.NAVER_CLIENT_ID
        response_type = "code"
        uri = main_domain + "/users/naver/callback/"
        state = settings.STATE
        url = "https://nid.naver.com/oauth2.0/authorize"
        return redirect(
            f'{url}?response_type={response_type}&client_id={client_id}&redirect_uri={uri}&state={state}'
        )


class NaverCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            # 네이버 로그인 Parameters
            grant_type = 'authorization_code'
            client_id = settings.NAVER_CLIENT_ID
            client_secret = settings.NAVER_CLIENT_SECRET
            code = request.GET.get('code')
            state = request.GET.get('state')

            parameters = f"grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}"

            # token request
            token_request = requests.get(
                f"https://nid.naver.com/oauth2.0/token?{parameters}"
            )

            token_response_json = token_request.json()
            error = token_response_json.get("error", None)

            if error is not None:
                raise JSONDecodeError(error)

            access_token = token_response_json.get("access_token")
            refresh_token = token_response_json.get("refresh_token")

            # User info get request
            user_info_request = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return Response({"message": "failed to get email."}, status=status.HTTP_400_BAD_REQUEST)
            user_info = user_info_request.json().get("response")
            email = user_info["email"]
            nickname = user_info["nickname"]

            if MyUser.objects.filter(nickname=nickname).exists():
                nickname = f"Naver_{email.split('@')[0]}"

            # User 의 email 을 받아오지 못한 경우
            if email is None:
                return Response({
                    "error": "네이버로 부터 이메일 정보를 받아올 수 없습니다."
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = MyUser.objects.get(email=email)
                data = {'access_token': access_token, 'code': code, 'nickname': nickname}
                # accept 에는 token 값이 json 형태로 들어온다({"key"}:"token value")
                # 여기서 오는 key 값은 authtoken_token에 저장된다.
                accept = requests.post(
                    f"{main_domain}/users/naver/success/", data=data
                )
                # 만약 token 요청이 제대로 이루어지지 않으면 오류처리
                if accept.status_code != 200:
                    return Response({"error": "회원가입 하는데 실패했습니다."}, status=accept.status_code)
                return Response(accept.json(), status=status.HTTP_200_OK)

            except MyUser.DoesNotExist:
                data = {'access_token': access_token, 'code': code, 'nickname': nickname}
                accept = requests.post(
                    f"{main_domain}/users/naver/success/", data=data
                )
                # token 발급
                return Response(accept.json(), status=status.HTTP_200_OK)

        except:
            return Response({
                "error": "error",
            }, status=status.HTTP_404_NOT_FOUND)


class NaverToDjLoginView(SocialLoginView):
    adapter_class = naver_views.NaverOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs).data
        profile = Profile.objects.get(user=self.request.user)
        social_user = profile.user
        social_user.location = "거주지_선택"
        social_user.nickname = request.data.get('nickname')
        profile.location = "거주지_선택"
        profile.nickname = request.data.get('nickname')
        social_user.save()
        profile.save()
        additional_data = {
            "user_id": profile.pk
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
            return Response({'message': '해당 지역에 매핑되는 잔액조회 사이트가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
