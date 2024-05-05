import os

from django.shortcuts import render
import requests

from .models import DisplayMessage
from .forms import PostMessageForm


SITE_NAME = "FastAPI-AWS-Django-GCP"
URL = "https://peil328b55.execute-api.eu-west-2.amazonaws.com"
LIMIT = 20


def index(request):
    data = requests.get(os.path.join(URL, f"message?limit={LIMIT}"))
    message_list = [DisplayMessage.create(**x) for x in data.json()]
    context = {"message_list": message_list,
               "PostMessageForm": PostMessageForm(),
               "swagger_url": os.path.join(URL, "docs"),
               "site_name": SITE_NAME}
    if request.method == "POST":
        message = PostMessageForm(request.POST)
        if message.is_valid():
            x = requests.post(os.path.join(URL, "message"),
                              json=message.cleaned_data)
            print(x.status_code)
        else:
            context["errors"] = "Error: please check the form and retry."
    return render(request, "app/index.html", context)


def message_detail(request, message_id: str):
    data = requests.get(os.path.join(URL, "message", message_id))
    message = DisplayMessage.create(**data.json())
    return render(request, "app/message_detail.html",
                  {"message": message,
                   "site_name": SITE_NAME})
