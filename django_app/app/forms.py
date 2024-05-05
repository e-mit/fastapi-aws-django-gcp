from django.forms import ModelForm

from .models import PostMessage


class PostMessageForm(ModelForm):
    class Meta:
        model = PostMessage
        fields = ["name", "subject", "text"]
