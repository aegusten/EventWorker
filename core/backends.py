from django.contrib.auth.backends import BaseBackend
from users.models import Applicant, Organization

class ApplicantBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Applicant.objects.get(id_number=username)
            if user.check_password(password):
                return user
        except Applicant.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Applicant.objects.get(pk=user_id)
        except Applicant.DoesNotExist:
            return None

class OrganizationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Organization.objects.get(license_number=username)
            if user.check_password(password):
                return user
        except Organization.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Organization.objects.get(pk=user_id)
        except Organization.DoesNotExist:
            return None