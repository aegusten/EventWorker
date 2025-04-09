from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, id_number, full_name, password=None, **extra_fields):
        if not id_number:
            raise ValueError("The ID number must be set")
        extra_fields.setdefault('is_active', True)
        user = self.model(id_number=id_number, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(id_number, full_name, password, **extra_fields)
