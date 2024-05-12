from datetime import datetime, timezone

from django.db.models import Model, CharField, DateTimeField, IntegerField

MAX_NAME_LENGTH = 20
MAX_SUBJECT_LENGTH = 40
MAX_MESSAGE_LENGTH = 200
MAX_ID_LENGTH = 39  # This is a 128-bit number


class PostMessage(Model):
    name: CharField = CharField(max_length=MAX_NAME_LENGTH)
    subject: CharField = CharField(max_length=MAX_SUBJECT_LENGTH)
    text: CharField = CharField(max_length=MAX_MESSAGE_LENGTH)


class DisplayMessage(Model):
    name: CharField = CharField(max_length=MAX_NAME_LENGTH)
    subject: CharField = CharField(max_length=MAX_SUBJECT_LENGTH)
    text: CharField = CharField(max_length=MAX_MESSAGE_LENGTH)
    timestamp: DateTimeField = DateTimeField("Date posted")
    timestamp_ms: IntegerField = IntegerField()
    id: CharField = CharField(max_length=MAX_ID_LENGTH, primary_key=True)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, **kwargs):
        """Create and return instance object, saving in database if needed."""
        try:
            return cls.objects.get(id=kwargs['id'])
        except cls.DoesNotExist:
            timestamp = datetime.fromtimestamp(
                kwargs['timestamp_ms']/1000.0, tz=timezone.utc)
            return cls.objects.update_or_create(
                timestamp=timestamp, **kwargs)[0]
