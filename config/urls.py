from django.contrib import admin
from django.urls import path, include, re_path

from .settings import MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(  # api 문서 설명
    openapi.Info(
        title="Underwater(언더워터) API",
        default_version="v1",
        description="팀 수건 Underwater 프로젝트 API 문서",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [  # BaseURL 다음 입력할 수 있는 url
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('stores/', include('stores.urls')),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)  # 미디어 경로


urlpatterns += [  # api 문서 경로
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]