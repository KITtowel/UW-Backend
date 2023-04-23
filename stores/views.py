from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StoreDaegu
from .serializers import StoreListSerializer
from rest_framework.pagination import PageNumberPagination
from operator import itemgetter


class StorePagination(PageNumberPagination):
    page_size = 10  # 한 페이지에 나타내는 가게 개수
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):  # 최대 페이지 10페이지로 제한
        response = super().get_paginated_response(data)
        if self.page.number == 10:
            response.data['next'] = None
        return response


class StoreListView(APIView):
    pagination_class = StorePagination

    def get(self, request):
        try:
            user_latitude = float(request.data.get('latitude'))
            user_longitude = float(request.data.get('longitude'))
        except ValueError:
            return Response(status=400, data={'message': '잘못된 값이 전달되었습니다.'})

        store = StoreDaegu.objects.all()
        serializer = StoreListSerializer(store, many=True, context={'user_latitude': user_latitude, 'user_longitude': user_longitude})
        sorted_data = sorted(serializer.data, key=itemgetter('distance'))
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(sorted_data, request)

        current_page = paginator.page.number
        if current_page > 10:
            return Response(status=404, data={'message': '최대 페이지를 초과하였습니다.'})

        return paginator.get_paginated_response(result_page)

