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
