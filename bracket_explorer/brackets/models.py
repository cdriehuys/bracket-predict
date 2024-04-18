import random
import sys
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from brackets import managers


class TrackedModel(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, verbose_name=_("ID"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    class Meta:
        abstract = True


class User(TrackedModel, AbstractBaseUser, PermissionsMixin):  # noqa: DJ008
    email = models.EmailField(unique=True, verbose_name=_("email"))

    is_active = models.BooleanField(
        default=True,
        help_text=_("Only active users are able to log in."),
        verbose_name=_("is active"),
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_("Staff users can access the admin site."),
        verbose_name=_("is staff"),
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text=_("Super users are implicitly granted all permissions."),
        verbose_name=_("is superuser"),
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    objects = managers.UserManager()

    class Meta:
        ordering = ("id",)
        verbose_name = _("user")
        verbose_name_plural = _("users")


def generate_random_seed() -> int:
    return random.randrange(sys.maxsize)


class Bracket(TrackedModel):
    """
    A bracket prediction.
    """

    owner = models.ForeignKey(
        User,
        help_text=_("The user who owns the bracket."),
        on_delete=models.CASCADE,
        related_name="brackets",
        related_query_name="bracket",
        verbose_name=_("owner"),
    )
    name = models.CharField(
        help_text=_("A name to identify the bracket."), max_length=100
    )

    random_seed = models.BigIntegerField(
        default=generate_random_seed,
        help_text=_(
            "The seed used to prime the random number generator for the "
            "bracket predictor."
        ),
    )

    def __str__(self) -> str:
        return f"bracket '{self.name}'"
