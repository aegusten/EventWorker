from django.contrib.auth.backends import BaseBackend
from users.models import Applicant, Organization

class ApplicantOrOrgBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Applicant.objects.get(id_number=username)
        except Applicant.DoesNotExist:
            try:
                user = Organization.objects.get(license_number=username)
            except Organization.DoesNotExist:
                return None
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        from users.models import Applicant, Organization
        try:
            return Applicant.objects.get(pk=user_id)
        except Applicant.DoesNotExist:
            try:
                return Organization.objects.get(pk=user_id)
            except Organization.DoesNotExist:
                return None
