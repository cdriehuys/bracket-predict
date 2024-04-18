from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str = None, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True

        return self.create_user(email, password, **kwargs)
