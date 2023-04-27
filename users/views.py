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