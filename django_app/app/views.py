import os

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.urls import reverse
import requests

from .models import DisplayMessage
from .forms import PostMessageForm


SITE_NAME = "FastAPI-AWS-Django-GCP"
API_URL = os.environ['API_URL']
MESSAGE_DISPLAY_LIMIT = 20


def index(request):
    data = requests.get(
        os.path.join(API_URL, f"message?limit={MESSAGE_DISPLAY_LIMIT}"))
    message_list = [DisplayMessage.create(**x) for x in data.json()]
    context = {"message_list": message_list,
               "PostMessageForm": PostMessageForm(),
               "swagger_url": os.path.join(API_URL, "docs"),
               "site_name": SITE_NAME}
    if request.method == "POST":
        message = PostMessageForm(request.POST)
        if message.is_valid():
            data = requests.post(os.path.join(API_URL, "message"),
                                 json=message.cleaned_data)
            message = DisplayMessage.create(**data.json())
            return HttpResponseRedirect(reverse("app:message_detail",
                                                args=(message.id,)))
        else:
            context["errors"] = "Error: please check the form and retry."
    return render(request, "app/index.html", context)


def message_detail(request, message_id: str):
    if request.method == "GET":
        try:
            message = DisplayMessage.objects.get(id=message_id)
        except DisplayMessage.DoesNotExist:
            response = requests.get(
                os.path.join(API_URL, "message", message_id))
            if response.status_code == int(requests.codes.not_found):
                raise Http404("Message not found")
            message = DisplayMessage.create(**response.json())
        return render(request, "app/message_detail.html",
                      {"message": message, "site_name": SITE_NAME})
    elif request.method == "DELETE":
        response = requests.delete(
            os.path.join(API_URL, "message", message_id))
        DisplayMessage.objects.filter(id=message_id).delete()
        return HttpResponse()
