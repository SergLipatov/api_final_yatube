from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение, позволяющее только авторам объекта редактировать его."""

    def has_object_permission(self, request, view, authored_item):
        return (request.method in permissions.SAFE_METHODS
                or authored_item.author == request.user)
