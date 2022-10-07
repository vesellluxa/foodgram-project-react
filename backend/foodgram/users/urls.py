from django.urls import include, path
from rest_framework import routers

from .views import FoodUserViewSet, SubscriptionsViewSet, logout, obtain_token

router = routers.DefaultRouter()
router.register(
    'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions')
router.register('users', FoodUserViewSet, basename='users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/token/login/', obtain_token, name='login'),
    path('api/auth/token/logout/', logout, name='logout')
]
