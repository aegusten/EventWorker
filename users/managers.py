from django.contrib.auth.base_user import BaseUserManager

class ApplicantManager(BaseUserManager):
    def create_user(self, id_number, full_name, email, password=None, **extra_fields):
        if not id_number or not email:
            raise ValueError("Passport ID and email are required.")
        email = self.normalize_email(email)
        applicant = self.model(
            id_number=id_number,
            full_name=full_name,
            email=email,
            **extra_fields
        )
        applicant.set_password(password)
        applicant.save(using=self._db)
        return applicant

    def create_superuser(self, id_number, full_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(id_number, full_name, email, password, **extra_fields)


class OrganizationManager(BaseUserManager):
    def create_user(self, id_number, full_name, email, password=None, **extra_fields):
        if not id_number or not email:
            raise ValueError("Passport ID and email are required.")
        email = self.normalize_email(email)
        organization = self.model(
            id_number=id_number,
            full_name=full_name,
            email=email,
            **extra_fields
        )
        organization.set_password(password)
        organization.save(using=self._db)
        return organization

    def create_superuser(self, id_number, full_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(id_number, full_name, email, password, **extra_fields)
