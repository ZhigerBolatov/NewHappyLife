from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, iin, password, **extra_fields):
        user = self.model(iin=iin, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, iin, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(iin, password, **extra_fields)
