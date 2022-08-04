"""
Client api serializers
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from clients import models
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer to use with clients
    """
    class Meta:
        """
        Meta class
        """
        model = User
        fields = ['first_name', 'last_name', 'email']


class ClientSerializer(serializers.ModelSerializer):
    """
    Client serializer
    """

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    password = serializers.CharField(
        label='Senha', max_length=128, required=True, write_only=True,
        style={'input_type': 'password', 'placeholder': 'Password'})

    class Meta:
        """
        Meta class
        """
        model = models.Client
        fields = ['id', 'first_name', 'last_name', 'email', 'birth_date', 'cpf',
                  'cnpj', 'politically_exposed', 'password']

    def validate(self, attrs):
        """
        Email duplicates are not allowed
        """
        user = attrs.get('user')
        if user and user.get('email'):
            email = user.get('email')
            if User.objects.filter(email=email).count() > 0:
                raise serializers.ValidationError(
                    {'email': "A client with this email already exists"})
        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(
            username=user_data['email'][0:150], **user_data)
        password = validated_data.pop('password')
        user.set_password(password)
        user.save()

        if validated_data.get('cnpj'):
            # pylint: disable=no-member
            obj = models.Client.create_client(
                user, type=models.Client.Type.PJ, **validated_data)
        else:
            obj = models.Client.create_client(user, **validated_data)
        return obj

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            email = user_data.get('email')
            if email:
                User.objects.filter(pk=instance.user.pk).update(
                    username=email[0:150], **user_data)
            else:
                User.objects.filter(pk=instance.user.pk).update(**user_data)

        if validated_data:
            # pylint: disable=no-member
            models.Client.objects.filter(
                pk=instance.pk).update(**validated_data)

        instance.refresh_from_db()

        return instance
