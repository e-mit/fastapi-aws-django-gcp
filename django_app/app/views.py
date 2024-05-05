import os

from django.utils import timezone
from django.shortcuts import render
import requests

from .models import DisplayMessage
from .forms import PostMessageForm


test_message = DisplayMessage(name="bob", subject="hello",
                              text="Body text", id="12345",
                              timestamp=timezone.now().time())

URL = "https://peil328b55.execute-api.eu-west-2.amazonaws.com"


def index(request):
    data = requests.get(os.path.join(URL, "message"))
    message_list = [DisplayMessage.create(**x) for x in data.json()]
    context = {"message_list": message_list,
               "PostMessageForm": PostMessageForm()}
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
                  {"message": message})
