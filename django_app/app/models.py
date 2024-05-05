from django.db.models import Model, CharField, DateTimeField


MAX_NAME_LENGTH = 20
MAX_SUBJECT_LENGTH = 40
MAX_MESSAGE_LENGTH = 200


class PostMessage(Model):
    name: CharField = CharField(max_length=MAX_NAME_LENGTH)
    subject: CharField = CharField(max_length=MAX_SUBJECT_LENGTH)
    text: CharField = CharField(max_length=MAX_MESSAGE_LENGTH)


class DisplayMessage(Model):
    name: CharField = CharField(max_length=MAX_NAME_LENGTH)
    subject: CharField = CharField(max_length=MAX_SUBJECT_LENGTH)
    text: CharField = CharField(max_length=MAX_MESSAGE_LENGTH)
    timestamp: DateTimeField = DateTimeField("Date posted")
    id: CharField = CharField(max_length=100, primary_key=True)
