import random
import string
import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Profile
from .serializers import (
    PhoneSerializer,
    CodeSerializer,
    ProfileSerializer,
    InviteSerializer
)


class AuthRequestView(APIView):
    """Представление генерации кода"""
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']

            # Генерируем 4-значный код и сохраняем в сессии
            auth_code = ''.join(random.choices(string.digits, k=4))
            request.session['auth_phone'] = phone
            request.session['auth_code'] = auth_code
            request.session['auth_code_expires'] = time.time() + 120  # Код действителен 2 минуты

            # В реальном приложении здесь была бы отправка SMS
            print(f"Код подтверждения для {phone}: {auth_code}")  # Для тестирования

            time.sleep(2)  # Имитация задержки
            return Response({
                'message': 'Код отправлен',
                'debug': f'Код подтверждения для {phone}: {auth_code}'
            })

        return Response(serializer.errors, status=400)


class AuthVerifyView(APIView):
    """Представление авторизации"""
    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            stored_phone = request.session.get('auth_phone')
            stored_code = request.session.get('auth_code')
            expires = request.session.get('auth_code_expires', 0)

            # Проверяем срок действия кода
            if time.time() > expires:
                return Response({'error': 'Срок действия кода истек'}, status=400)

            # Проверяем совпадение кода
            if stored_code != code:
                return Response({'error': 'Неверный код подтверждения'}, status=400)

            # Создаем/получаем пользователя
            user, created = CustomUser.objects.get_or_create(phone=stored_phone)

            if not hasattr(user, 'profile'):
                profile = Profile.objects.create(user=user)
                profile.invite_code = Profile.generate_invite_code()
                profile.save()

            # Очищаем сессию
            request.session.pop('auth_phone', None)
            request.session.pop('auth_code', None)
            request.session.pop('auth_code_expires', None)

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Успешная авторизация',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })

        return Response(serializer.errors, status=400)


class ProfileView(APIView):
    """Представление профиля"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            # Если профиль не существует - создаем
            profile = Profile.objects.create(user=request.user)
            profile.invite_code = Profile.generate_invite_code()
            profile.save()

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class ActivateInviteView(APIView):
    """Представление активации инвайт-кода"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        if profile.activated_invite:
            return Response({'error': 'Вы уже активировали код'}, status=400)

        serializer = InviteSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = serializer.validated_data['invite_code']

            if invite_code == profile.invite_code:
                return Response({'error': 'Нельзя активировать свой код'}, status=400)

            try:
                referrer = Profile.objects.get(invite_code=invite_code)
                profile.activated_invite = referrer
                profile.save()
                return Response({'message': 'Код активирован'})
            except Profile.DoesNotExist:
                return Response({'error': 'Неверный код'}, status=400)
        return Response(serializer.errors, status=400)
