from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Пагинация применяется только если указаны параметры limit и offset
    """

    def get_paginated_response(self, data):
        # Стандартное поведение пагинации
        return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        # Получаем limit из запроса
        limit = request.query_params.get('limit', None)

        # Если limit не указан, отключаем пагинацию
        if limit is None:
            return None

        # Иначе используем стандартную пагинацию
        return super().paginate_queryset(queryset, request, view)
