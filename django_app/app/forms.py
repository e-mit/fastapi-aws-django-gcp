from django.forms import ModelForm

from .models import PostMessage


class PostMessageForm(ModelForm):
    """Define the form for posting a message."""

    def __init__(self, *args, **kwargs):
        """Remove the default colon from the form labels."""
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = PostMessage
        fields = ["name", "subject", "text"]
