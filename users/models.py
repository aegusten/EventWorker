from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    id_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=[('job_seeker', 'Job Seeker'), ('job_poster', 'Job Poster')]
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.id_number



class SecurityQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class UserSecurityAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_answers')
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.id_number} - {self.question_text}"


class ApplicantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education = models.TextField()
    cv = models.FileField(upload_to='cvs/')
    availability = models.CharField(max_length=20, choices=[('part-time', 'Part-time'), ('volunteer', 'Volunteer')])
    preferred_location = models.CharField(max_length=100)
    job_type_interest = models.CharField(max_length=20, choices=[('full-time', 'Full-time'), ('part-time', 'Part-time'), ('volunteer', 'Volunteer')])
    skills = models.TextField(blank=True)
    location_of_interest = models.CharField(max_length=100, blank=True)
    last_cv_update = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"ApplicantProfile: {self.user.full_name}"


class OrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100)
    company_name = models.CharField(max_length=255)
    establishment_date = models.DateField()
    location = models.CharField(max_length=100)
    achievements = models.TextField(blank=True)
    sector = models.CharField(
        max_length=50,
        choices=[
            ('IT', 'IT'),
            ('NGO', 'NGO'),
            ('Aviation', 'Aviation'),
            ('Business', 'Business'),
        ]
    )
    company_type = models.CharField(
        max_length=20,
        choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')]
    )

    def __str__(self):
        return f"OrganizationProfile: {self.company_name}"

