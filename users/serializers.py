from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .models import Profile, MyUser

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(
        help_text="닉네임(Unique)",
        required=True
    )
    email = serializers.EmailField(
        help_text="이메일(Unique)",
        required=True,
        validators=[UniqueValidator(queryset=MyUser.objects.all())],
    )
    password = serializers.CharField(
        help_text="비밀번호",
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(help_text="비밀번호 재입력", write_only=True, required=True)
    location = serializers.CharField(help_text="지역 선택", required=True)
    location2 = serializers.CharField(help_text="시/군 선택", required=False, allow_blank=True)

    class Meta:
        model = MyUser
        fields = ('nickname', 'username', 'password', 'password2', 'email', 'location', 'location2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        nickname = validated_data['nickname']
        if MyUser.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError(
                {"nickname": "이미 사용 중인 닉네임입니다."})
        user = MyUser.objects.create_user(
            nickname=nickname,
            username=validated_data['username'],
            email=validated_data['email'],
            location=validated_data['location'],
            location2=validated_data['location2']
        )

        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="아이디", required=True)
    password = serializers.CharField(help_text="비밀번호", required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {"error": "등록되지 않은 사용자이거나 아이디 또는 비밀번호가 틀렸습니다."})


class ProfileSerializer(serializers.ModelSerializer):
    location2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Profile
        fields = ("nickname", "location", "location2", "image")

    def update(self, instance, validated_data):
        if 'nickname' in validated_data:
            new_nickname = validated_data['nickname']
            existing_nicknames = Profile.objects.exclude(pk=instance.pk).values_list('nickname', flat=True)
            if new_nickname in existing_nicknames:
                raise serializers.ValidationError({'nickname': '이미 사용 중인 닉네임입니다.'})
        instance.location2 = validated_data.get('location2', instance.location2)
        instance.save()
        return super().update(instance, validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError('현재 비밀번호가 맞지 않습니다.')
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError('새로운 비밀번호 입력이 일치하지 않습니다.')
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()