from django.urls import include, path

urlpatterns = [
    path("v1/main/", include("main.urls")),
]
