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

    def post(self, request, pk):
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


# # kakao social
# def oauth(request):
#     code = request.GET['code']
#     print('code = ' + str(code))
#
#     secret_file = os.path.join(BASE_DIR, 'secrets.json')
#
#     with open(secret_file) as f:
#         secrets = json.loads(f.read())
#
#     def get_secret(setting, secrets=secrets):
#         try:
#             return secrets[setting]
#         except KeyError:
#             error_msg = "Set the {} environment variable".format(setting)
#             raise ImproperlyConfigured(error_msg)
#
#     KAKAO_CLIENT_ID = get_secret("KAKAO_CLIENT_ID")  # secrets.json에서 ID, Secret Key 받아옴
#     # KAKAO_CLIENT_SECRET = get_secret("KAKAO_CLIENT_SECRET")
#
#     redirect_uri = 'http://127.0.0.1:8000/user/login/kakao/callback'
#
#     # request로 받은 code로 access_token 받아오기
#     access_token_request_uri = 'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&'
#     access_token_request_uri += 'client_id=' + KAKAO_CLIENT_ID
#     access_token_request_uri += '&code=' + code
#     access_token_request_uri += '&redirect_uri=' + redirect_uri
#
#     access_token_request_uri_data = requests.get(access_token_request_uri)
#     json_data = access_token_request_uri_data.json()  # json 형태로 데이터 저장
#     access_token = json_data['access_token']  # 액세스 토큰 꺼내와서 저장
#
#     # 프로필 정보 받아오기
#     headers = ({'Authorization': f"Bearer {access_token}"})  # header에 꼭 설정해야 함
#
#     user_profile_info_uri = 'https://kapi.kakao.com/v2/user/me'
#     user_profile_info = requests.get(user_profile_info_uri, headers=headers)
#
#     json_data = user_profile_info.json()
#
#     # 닉네임과 이메일 데이터 가져옴
#     nickname = json_data['kakao_account']['profile']['nickname']
#     email = json_data['kakao_account']['email']
#
#     # 데이터베이스에 이미 저장되어있는 회원이면, user에 회원 저장
#     if User.objects.filter(email=email).exists():
#         user = User.objects.get(email=email)
#     # 회원가입인 경우
#     else:
#         user = User.objects.create(
#             email=email,
#             nickname=nickname
#         )
#         user.save()
#
#     # 토큰 발행
#     payload = JWT_PAYLOAD_HANDLER(user)
#     jwt_token = JWT_ENCODE_HANDLER(payload)
#
#     response = {
#         'success': True,
#         'token': jwt_token
#     }
#
#     return Response(response, status=200)