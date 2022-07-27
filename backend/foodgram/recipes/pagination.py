"""Кастомные настройки пагинации приложения API."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings


class ApiPagination(PageNumberPagination):
    """Кастомный класс пагинации.
    page_size - страницы по умолчанию.
    """
    page_size = api_settings.PAGE_SIZE
