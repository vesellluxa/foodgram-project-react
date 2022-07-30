from rest_framework import mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from recipes.permissions import IsAuthenticatedOrRegister
from recipes.pagination import ApiPagination
from recipes.serializers import FoodUserSerializer, SubscriptionSerializer
from users.models import Follow, FoodUser
from users.serializers import FollowSerializer, RegistrationSerializer
from users.serializers import SetPasswordSerializer, TokenObtainSerializer


class FoodUserViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    serializer_class = FoodUserSerializer
    queryset = FoodUser.objects.all()
    permission_classes = (IsAuthenticatedOrRegister, )
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
        serializer = SetPasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.set_password()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           GenericViewSet):
    pagination_class = ApiPagination
    queryset = FoodUser.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(id__in=self.request.user.followings())


class FollowViewSet(mixins.DestroyModelMixin,
                    mixins.CreateModelMixin,
                    GenericViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    pagination_class = ApiPagination


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.get_or_create_token()
    return Response(
        data={"auth_token": f"{token}"},
        status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)
