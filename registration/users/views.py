import random
import string
import time

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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


# Представления для шаблонов
def index(request):
    return render(request, 'users/index.html')


@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        profile.invite_code = Profile.generate_invite_code()
        profile.save()

    # Получаем список рефералов
    referrals = [ref.user.phone for ref in profile.referrals.select_related('user').all()]

    return render(request, 'users/profile.html', {
        'profile': profile,
        'referrals': referrals,
        'activated_invite_code': profile.activated_invite.invite_code if profile.activated_invite else None
    })


def phone_auth(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        request.session['auth_phone'] = phone

        auth_code = ''.join(random.choices(string.digits, k=4))
        request.session['auth_code'] = auth_code
        request.session['auth_code_expires'] = time.time() + 120

        print(f"Код подтверждения для {phone}: {auth_code}")
        time.sleep(2)

        messages.info(request, f'Код подтверждения отправлен на номер {phone}')
        return redirect('verify_code')

    return render(request, 'users/phone_auth.html')


def verify_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        stored_phone = request.session.get('auth_phone')
        stored_code = request.session.get('auth_code')
        expires = request.session.get('auth_code_expires', 0)

        if time.time() > expires:
            messages.error(request, 'Срок действия кода истек')
            return redirect('phone_auth')

        if stored_code != code:
            messages.error(request, 'Неверный код подтверждения')
            return redirect('verify_code')

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

        # Логиним пользователя
        from django.contrib.auth import login
        login(request, user)

        messages.success(request, 'Успешная авторизация!')
        return redirect('profile_view')

    return render(request, 'users/verify_code.html')


@login_required
def activate_invite(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        profile = request.user.profile

        if profile.activated_invite:
            messages.error(request, 'Вы уже активировали код')
            return redirect('profile_view')

        if invite_code == profile.invite_code:
            messages.error(request, 'Нельзя активировать свой код')
            return redirect('profile_view')

        try:
            referrer = Profile.objects.get(invite_code=invite_code)
            profile.activated_invite = referrer
            profile.save()
            messages.success(request, 'Код успешно активирован!')
        except Profile.DoesNotExist:
            messages.error(request, 'Неверный инвайт-код')

        return redirect('profile_view')

    return redirect('profile_view')
