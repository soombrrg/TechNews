from behaviors.behaviors import Authored, Published, Slugged, Timestamped
from django.db import models


class TimeStampedModel(Timestamped):
    class Meta:
        abstract = True


class AuthoredModel(Authored):
    class Meta:
        abstract = True


class SluggedModel(Slugged):
    class Meta:
        abstract = True


class PublishedModel(Published):
    DRAFT = "d"
    PUBLISHED = "p"

    PUBLICATION_STATUS_CHOICES = (
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
    )

    publication_status = models.CharField(
        "Publication Status",
        max_length=1,
        choices=PUBLICATION_STATUS_CHOICES,
        default=PUBLISHED,  # overriding default
    )

    class Meta:
        abstract = True
