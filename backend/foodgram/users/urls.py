from django.urls import include, path
from rest_framework import routers
from users.views import (FoodUserViewSet, SubscriptionsViewSet, logout,
                         obtain_token)

router_v1 = routers.DefaultRouter()
router_v1.register(
    'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions')
router_v1.register('users', FoodUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('api/auth/token/login/', obtain_token),
    path('api/auth/token/logout/', logout)
]
