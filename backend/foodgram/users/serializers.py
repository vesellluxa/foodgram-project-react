from rest_framework import serializers
from users.models import Follow, FoodUser


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')

    def create(self, validated_data):
        validated_data['password'] = self.context['request'].data.get(
            'password')
        user = self.Meta.model.objects.create_user(**validated_data)
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
        return self.Meta.model.is_following(
            self=self.context.get('request').user, instance=instance)


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
