from django.urls import path

from . import views


app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("message/<int:message_id>/", views.message_detail,
         name="message_detail")
]
