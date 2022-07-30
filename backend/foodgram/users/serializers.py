from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Favourite, ShoppingList
from users.models import Follow, FoodUser


class TokenObtainSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        email = data['email']
        if not FoodUser.objects.filter(email=email).exists():
            raise ValidationError('Eamil is invalid')
        user = FoodUser.objects.get(email=email)
        password = data['password']
        if not user.check_password(password):
            raise ValidationError('Password is Invalid')
        return data

    def get_or_create_token(self):
        user = FoodUser.objects.get(email=self.data['email'])
        token = Token.objects.get_or_create(user=user)
        return token[0]


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        current_password = data['current_password']
        if not user.check_password(current_password):
            raise ValidationError('Current_password is invalid')
        new_password = data['new_password']
        validate_password(new_password)
        return data

    def set_password(self):
        password = self.data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')

    def create(self, validated_data):
        validated_data['password'] = self.context['request'].data.get(
            'password')
        user = self.Meta.model.objects.create_user(**validated_data)
        ShoppingList.objects.create(owner=user)
        Favourite.objects.create(owner=user)
        return user


class FoodUserSerializer(RegistrationSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')

    def get_is_subscribed(self, instance):
        return self.Meta.model.followings(
            self=self.context.get('request').user)


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
