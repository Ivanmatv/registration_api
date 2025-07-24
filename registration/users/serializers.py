from rest_framework import serializers
from django.core.validators import RegexValidator

from .models import Profile


class PhoneSerializer(serializers.Serializer):
    """Сериализатор номера телефона"""
    phone = serializers.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Некорректный номер телефона')]
    )


class CodeSerializer(serializers.Serializer):
    """Сериализатор кода"""
    code = serializers.CharField(max_length=4)


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""
    phone = serializers.CharField(source='user.phone')
    referrals = serializers.SerializerMethodField()
    activated_invite_code = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['phone', 'invite_code', 'activated_invite_code', 'referrals']

    def get_referrals(self, obj):
        return [ref.user.phone for ref in obj.referrals.select_related('user').all()]

    def get_activated_invite_code(self, obj):
        return obj.activated_invite.invite_code if obj.activated_invite else None


class InviteSerializer(serializers.Serializer):
    """Сериализатор инвайт-кода """
    invite_code = serializers.CharField(
        max_length=6,
        min_length=6,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9]{6}$',
                message="Инвайт-код должен состоять ровно из 6 букв или цифр"
            )
        ]
    )
