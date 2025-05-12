from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, mixins
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Post, Group
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    PostSerializer, GroupSerializer, CommentSerializer, FollowSerializer
)


class AuthorizedViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet с настройками авторизации."""

    permission_classes = (IsAuthorOrReadOnly,)


class PostViewSet(AuthorizedViewSet):
    """
    Вьюсет для управления постами.

    Предоставляет CRUD-операции для модели Post.
    Доступ к изменению постов имеет только их автор.
    Реализована пагинация и фильтрация по группам.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('group',)

    def perform_create(self, serializer):
        """Создаёт новый пост с текущим пользователем в качестве автора."""
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для работы с группами.

    Предоставляет только операции чтения для модели Group.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(AuthorizedViewSet):
    """
    Вьюсет для управления комментариями.

    Предоставляет CRUD-операции для комментариев к конкретному посту.
    Доступ к изменению комментариев имеет только их автор.
    """

    serializer_class = CommentSerializer

    def _get_post(self):
        """Приватный метод для получения объекта поста.

        Returns:
            Post: Объект поста по ID из URL-параметров

        Raises:
            Http404: Если пост не найден

        """
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_queryset(self):
        """Возвращает все комментарии для указанного поста."""
        return self._get_post().comments.all()

    def perform_create(self, serializer):
        """Создаёт комментарий с текущим пользователем в качестве автора."""
        serializer.save(author=self.request.user, post=self._get_post())


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Вьюсет для управления подписками.

    Позволяет пользователям создавать подписки и просматривать свои подписки.
    Доступно только авторизованным пользователям.
    Поддерживает поиск по имени пользователя, на которого подписываются.
    """

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Возвращает все подписки текущего пользователя."""
        return self.request.user.subscriptions.all()

    def perform_create(self, serializer):
        """Создаёт подписку с текущим пользователем в качестве подписчика."""
        serializer.save(user=self.request.user)
