from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de profil / mise à jour.

    Le rôle n'est jamais accepté en écriture ici : un utilisateur ne
    peut pas s'auto-promouvoir administrateur via le corps HTTP.
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "password",
        ]
        read_only_fields = [
            "id",
            "role",
        ]

    def create(self, validated_data):
        validated_data.pop("role", None)
        password = validated_data.pop("password", None)

        return User.objects.create_user(
            password=password,
            **validated_data,
        )

    def update(self, instance, validated_data):
        validated_data.pop("role", None)
        password = validated_data.pop("password", None)

        for champ, valeur in validated_data.items():
            setattr(instance, champ, valeur)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserCreateSerializer(UserSerializer):
    """
    Création de compte par un administrateur.

    Le rôle peut être fixé à la création uniquement, jamais ensuite
    par l'utilisateur lui-même.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        return User.objects.create_user(
            password=password,
            **validated_data,
        )


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        if getattr(self.user, "role", None) != User.Role.ADMIN:
            raise AuthenticationFailed(
                "Accès refusé. Seuls les administrateurs peuvent se connecter."
            )

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
        }

        return data
