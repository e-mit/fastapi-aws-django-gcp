from django.urls import include, path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", include("app.urls")),
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('favicon.ico')))
]
