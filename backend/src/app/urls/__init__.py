from django.conf import settings
from django.contrib import admin
from django.urls import include, path

api = [
    path("v1/", include(("app.urls.v1", "v1"), namespace="v1")),
]

urlpatterns = [
    path("api/", include(api)),
    path("admin/", admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar  # type: ignore
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # type: ignore
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # type: ignore
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
