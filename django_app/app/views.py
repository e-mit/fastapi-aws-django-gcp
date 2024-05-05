from django.utils import timezone
from django.shortcuts import render

from .models import DisplayMessage
from .forms import PostMessageForm


test_message = DisplayMessage(name="bob", subject="hello",
                              text="Body text", id="12345",
                              timestamp=timezone.now().time())


def index(request):
    context = {"message_list": [test_message, test_message, test_message],
               "PostMessageForm": PostMessageForm()}
    if request.method == "POST":
        message = PostMessageForm(request.POST)
        if message.is_valid():
            print(message.cleaned_data)
        else:
            context["errors"] = "Error: please check the form and retry."
    return render(request, "app/index.html", context)


def message_detail(request, message_id: int):
    print(f"Get message {message_id}.")
    return render(request, "app/message_detail.html",
                  {"message": test_message})
