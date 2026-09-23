from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):

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
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for champ, valeur in validated_data.items():
            setattr(instance, champ, valeur)

        if password:
            instance.set_password(password)
        instance.save()

        return instance

class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # On ajoute les informations de l'utilisateur
        # dans la réponse du login.
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
        }

        return data