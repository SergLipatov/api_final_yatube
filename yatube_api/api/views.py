from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, mixins

from posts.models import Post, Group, Follow
from .serializers import (
    PostSerializer, GroupSerializer, CommentSerializer, FollowSerializer
)
from .permissions import IsAuthorOrReadOnly
from .pagination import CustomLimitOffsetPagination


class PostViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления постами.

    Предоставляет CRUD-операции для модели Post.
    Доступ к изменению постов имеет только их автор.
    Реализована пагинация и фильтрация по группам.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomLimitOffsetPagination
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


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления комментариями.

    Предоставляет CRUD-операции для комментариев к конкретному посту.
    Доступ к изменению комментариев имеет только их автор.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        """Возвращает все комментарии для указанного поста."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.all()

    def perform_create(self, serializer):
        """Создаёт комментарий с текущим пользователем в качестве автора."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)


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
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Создаёт подписку с текущим пользователем в качестве подписчика."""
        serializer.save(user=self.request.user)
