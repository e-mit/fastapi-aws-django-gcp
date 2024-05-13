from django.urls import path

from . import views


app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("message/<str:message_id>/", views.message_detail,  # type:ignore
         name="message_detail")
]
