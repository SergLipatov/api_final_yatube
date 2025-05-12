from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from posts.models import Comment, Follow, Group, Post, User


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Post (Пост).

    Предоставляет преобразование данных модели Post в формат JSON и обратно,
    с отображением автора поста через его имя пользователя.
    """

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment (Комментарий).

    Обеспечивает сериализацию и десериализацию объектов Comment,
    показывая автора комментария через его имя пользователя.
    Пост, к которому относится комментарий, доступен только для чтения.
    """

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('post',)
        model = Comment


class GroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Group (Группа).

    Обеспечивает преобразование данных модели Group в JSON-формат и обратно,
    включая все поля модели.
    """

    class Meta:
        fields = '__all__'
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Follow (Подписка).

    Позволяет пользователям подписываться на авторов.
    Содержит проверки уникальности подписки и запрет подписки на самого себя.
    """

    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate_following(self, target_user):
        """
        Проверяет, что пользователь не пытается подписаться на самого себя.

        Args:
            target_user: Объект пользователя, на которого происходит подписка.

        Returns:
            Объект пользователя, если проверка пройдена успешно.

        Raises:
            ValidationError: При попытке подписаться на самого себя.
        """
        if self.context['request'].user == target_user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return target_user
