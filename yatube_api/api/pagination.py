from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """Пагинация применяется только если указаны параметры limit и offset."""

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        limit = request.query_params.get('limit', None)

        if limit is None:
            return None

        return super().paginate_queryset(queryset, request, view)
