from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.owner


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_superuser)
                or request.user.is_authenticated
                )

    def has_object_permission(self, request, view, obj):
        return ((request.method in permissions.SAFE_METHODS)
                or (request.user == obj.author)
                or (request.user.is_authenticated
                    and request.user.is_superuser)
                )


class IsAuthenticatedOrRegister(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        return ((request.method in permissions.SAFE_METHODS)
                or (request.user == obj.author)
                or (request.user.is_authenticated
                    and request.user.is_superuser)
                )
