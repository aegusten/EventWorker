from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.views import LoginView
from django.urls import reverse

class ApplicantManager(BaseUserManager):
    def create_user(self, id_number, full_name, email, password=None, **extra_fields):
        if not id_number or not email:
            raise ValueError("ID Number and email are required.")
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
    def create_user(self, license_number, full_name, email, password=None, **extra_fields):
        if not license_number or not email:
            raise ValueError("License number and email are required.")
        email = self.normalize_email(email)
        organization = self.model(
            license_number=license_number,
            full_name=full_name,
            email=email,
            **extra_fields
        )
        organization.set_password(password)
        organization.save(using=self._db)
        return organization

    def create_superuser(self, license_number, full_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(license_number, full_name, email, password, **extra_fields)


class RoleBasedLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        # Redirect based on user type
        if hasattr(user, 'user_type') and user.user_type == 'organization':
            return reverse('org_dashboard')
        else:
            return reverse('applicant_dashboard')