from rest_framework import mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from recipes.pagination import ApiPagination
from recipes.serializers import FoodUserSerializer, SubscriptionSerializer
from users.models import Follow, FoodUser
from users.serializers import FollowSerializer, RegistrationSerializer


class FoodUserViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    serializer_class = FoodUserSerializer
    queryset = FoodUser.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = ApiPagination

    def create(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(
            data=request.data, context={
                "request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)

    @action(
        detail=True,
        methods=['DELETE', 'POST'],
        permission_classes=[IsAuthenticated, ],
    )
    def subscribe(self, request, pk):
        if request.method == 'POST':
            data = {
                "user": self.request.user.id,
                "following": pk
            }
            if Follow.objects.filter(
                    user=self.request.user.pk,
                    following=pk).exists():
                return Response(
                    {'errors': 'you already subscribed'},
                    status=status.HTTP_200_OK)
            serializer = FollowSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.serializer_class(
                FoodUser.objects.get(
                    pk=pk), context={
                    "request": request})
            return Response(data=serializer.data)
        follow = Follow.objects.filter(
            user=self.request.user.pk,
            following=pk).first()
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        current_password = request.data['current_password']
        user = self.request.user
        if user.check_password(current_password):
            user.set_password(request.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={
                "current_password":
                    "Password is invalid or new password is invalid"
            }
        )


class SubscriptionsViewSet(mixins.ListModelMixin,
                           GenericViewSet):
    pagination_class = ApiPagination
    queryset = FoodUser.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        not_following = []
        for user in self.queryset:
            if not self.request.user.is_following(user):
                not_following.append(user.username)
        queryset = self.queryset.exclude(username__in=not_following)
        return queryset


class FollowViewSet(mixins.DestroyModelMixin,
                    mixins.CreateModelMixin,
                    GenericViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    pagination_class = ApiPagination


@api_view(['POST'])
def obtain_token(request):
    user = FoodUser.objects.filter(email=request.data.get('email')).first()
    if user.check_password(request.data.get('password')):
        token = Token.objects.get_or_create(user=user)
        return Response(
            data={
                "auth_token": f"{token[0]}"},
            status=status.HTTP_201_CREATED)
    return Response('Not valid email or password')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)
