import os

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.urls import reverse
import requests

from .models import DisplayMessage
from .forms import PostMessageForm


SITE_NAME = "FastAPI-AWS-Django-GCP"
URL = "https://peil328b55.execute-api.eu-west-2.amazonaws.com"
MESSAGE_DISPLAY_LIMIT = 20


def index(request):
    data = requests.get(
        os.path.join(URL, f"message?limit={MESSAGE_DISPLAY_LIMIT}"))
    message_list = [DisplayMessage.create(**x) for x in data.json()]
    context = {"message_list": message_list,
               "PostMessageForm": PostMessageForm(),
               "swagger_url": os.path.join(URL, "docs"),
               "site_name": SITE_NAME}
    if request.method == "POST":
        message = PostMessageForm(request.POST)
        if message.is_valid():
            data = requests.post(os.path.join(URL, "message"),
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
            response = requests.get(os.path.join(URL, "message", message_id))
            if response.status_code == int(requests.codes.not_found):
                raise Http404("Message not found")
            message = DisplayMessage.create(**response.json())
        return render(request, "app/message_detail.html",
                      {"message": message, "site_name": SITE_NAME})
    elif request.method == "DELETE":
        response = requests.delete(os.path.join(URL, "message", message_id))
        DisplayMessage.objects.filter(id=message_id).delete()
        return HttpResponse()
