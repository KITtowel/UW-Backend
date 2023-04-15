from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate

from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from .models import Profile, MyUser


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


class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
