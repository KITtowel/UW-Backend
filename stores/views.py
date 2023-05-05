from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import StoreDaegu, Review, Report
from users.models import Profile
from .serializers import StoreListSerializer, StoreDetailSerializer, ReviewCreateSerializer, ReviewSerializer, \
    ReviewListSerializer
from rest_framework.pagination import PageNumberPagination
from operator import itemgetter
from rest_framework import generics, status, permissions
from django.utils import timezone
from django.db.models import Avg


class StorePagination(PageNumberPagination):
    page_size = 10  # 한 페이지에 나타내는 가게 개수
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):  # 최대 페이지 10페이지로 제한
        response = super().get_paginated_response(data)
        if self.page.number == 10:
            response.data['next'] = None
        return response


# 가까운 거리순으로 가맹점 리스트 반환
class StoreListView(APIView):
    pagination_class = StorePagination

    def post(self, request):
        try:
            user_latitude = float(request.data.get('latitude'))  # 중앙 위도
            user_longitude = float(request.data.get('longitude'))  # 중앙 경도
            ne_latitude = float(request.data.get('ne_latitude'))  # 북동 위도
            ne_longitude = float(request.data.get('ne_longitude'))  # 북동 경도
            sw_latitude = float(request.data.get('sw_latitude'))  # 남서 위도
            sw_longitude = float(request.data.get('sw_longitude'))  # 남서 경도
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': '잘못된 값이 전달되었습니다.'})

        # store = StoreDaegu.objects.all()
        # 북동 좌표와 남서 좌표 안에 있는 가게들만 필터링
        store = StoreDaegu.objects.filter(
            latitude__gte=sw_latitude, latitude__lte=ne_latitude,
            longitude__gte=sw_longitude, longitude__lte=ne_longitude,
        )

        serializer = StoreListSerializer(store, many=True,
                                         context={'user_latitude': user_latitude, 'user_longitude': user_longitude})
        sorted_data = sorted(serializer.data, key=itemgetter('distance'))
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(sorted_data, request)

        current_page = paginator.page.number
        if current_page > 10:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': '최대 페이지를 초과하였습니다.'})

        return paginator.get_paginated_response(result_page)


# 가맹점 좋아요 기능
class StoreLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            store = StoreDaegu.objects.get(store_id=pk)
        except StoreDaegu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': '가맹점 정보가 없습니다.'})
        if request.user in store.likes.all():
            store.likes.remove(request.user)
            liked = False
            message = '좋아요가 취소되었습니다.'
        else:
            store.likes.add(request.user)
            liked = True
            message = '좋아요가 등록되었습니다.'
        return Response(status=status.HTTP_200_OK, data={'message': message, 'liked': liked, })


# 사용자가 좋아요 누른 가맹점 리스트 반환
class LikedStoreListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StorePagination

    def post(self, request):
        user = request.user
        liked_stores = user.like_posts.all()
        serializer = StoreListSerializer(liked_stores, many=True)
        sorted_data = sorted(serializer.data, key=itemgetter('store_name'))  # 가맹점 이름 순으로 정렬
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(sorted_data, request)
        response = paginator.get_paginated_response(paginated_data)
        if paginator.page.number > paginator.page.paginator.num_pages:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': '최대 페이지를 초과하였습니다.'})
        return response


# 좋아요 개수가 많은 순으로 가맹점 리스트 반환
class LikedCountStoreListView(APIView):
    pagination_class = StorePagination

    def post(self, request):
        store = StoreDaegu.objects.all()
        serializer = StoreListSerializer(store, many=True)
        # 좋아요 개수가 같으면 가맹점 이름 순으로 정렬
        sorted_data = sorted(serializer.data, key=lambda x: (-x['likes_count'], x['store_name']))
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(sorted_data, request)

        current_page = paginator.page.number
        if current_page > 10:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': '최대 페이지를 초과하였습니다.'})

        return paginator.get_paginated_response(result_page)


# 가맹점 상세보기
class StoreDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, store_id):
        try:
            store = StoreDaegu.objects.get(store_id=store_id)
        except StoreDaegu.DoesNotExist:
            return Response({'message': '가맹점이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StoreDetailSerializer(store, context={'request': request})
        return Response(serializer.data)


# 후기글 작성
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        store_id = self.kwargs.get('store_id')
        store = StoreDaegu.objects.get(pk=store_id)
        serializer.save(author=self.request.user, profile=profile, store=store)
        reviews = Review.objects.filter(store=store)
        rating_mean = reviews.aggregate(Avg('rating'))['rating__avg']
        store.rating_mean = rating_mean
        store.save(update_fields=['rating_mean'])


# 후기글 조회, 수정, 삭제
class ReviewView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': '수정이 완료되었습니다.'}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.validated_data['modified_date'] = timezone.now()
        serializer.save(author=self.request.user)
        store = serializer.instance.store
        reviews = Review.objects.filter(store=store)
        rating_mean = reviews.aggregate(Avg('rating'))['rating__avg']
        store.rating_mean = rating_mean
        store.save(update_fields=['rating_mean'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        store = instance.store
        self.perform_destroy(instance)
        reviews = Review.objects.filter(store=store)
        rating_mean = reviews.aggregate(Avg('rating'))['rating__avg']
        store.rating_mean = rating_mean if rating_mean else 0
        store.save(update_fields=['rating_mean'])
        return Response({'message': '후기글이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)


# 평균 평점이 높은 순으로 가맹점 리스트 반환
class MeanRatingStoreListView(APIView):
    pagination_class = StorePagination

    def post(self, request):
        store = StoreDaegu.objects.all()
        serializer = StoreListSerializer(store, many=True)
        # 평균 평점이 같으면 가맹점 이름 순으로 정렬
        sorted_data = sorted(serializer.data, key=lambda x: (-x['rating_mean'], x['store_name']))
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(sorted_data, request)

        current_page = paginator.page.number
        if current_page > 10:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': '최대 페이지를 초과하였습니다.'})

        return paginator.get_paginated_response(result_page)


# 사용자가 작성한 후기글 리스트 반환
class UserReviewListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StorePagination

    def post(self, request):
        reviewed_stores = Review.objects.filter(author=request.user)
        serializer = ReviewListSerializer(reviewed_stores, many=True)
        sorted_data = sorted(serializer.data, key=itemgetter('store_name'))  # 가맹점 이름 순으로 정렬
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(sorted_data, request)
        response = paginator.get_paginated_response(paginated_data)
        if paginator.page.number > paginator.page.paginator.num_pages:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': '최대 페이지를 초과하였습니다.'})
        return response


class ReviewReportView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_object(self, pk):
        try:
            return self.queryset.get(pk=pk)
        except Review.DoesNotExist:
            raise Response({'message': '없는 후기글입니다.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        review = self.get_object(pk)
        if request.user != review.author:
            report_queryset = Report.objects.filter(review=review)
            if report_queryset.filter(reporter=request.user).exists():
                return Response({'message': '이미 신고한 후기입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                report = Report(review=review, store=review.store, reporter=request.user, reason=request.data.get('reason'))
                report.save()
                review.reported_num += 1
                review.save()
                return Response({'message': '신고가 정상적으로 접수되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '자신의 게시글은 신고할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
