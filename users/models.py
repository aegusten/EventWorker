from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .managers import ApplicantManager, OrganizationManager


class Applicant(AbstractBaseUser, PermissionsMixin):
    id_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    age = models.PositiveIntegerField()
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    education = models.TextField()
    cv = models.FileField(upload_to='cvs/')
    availability = models.CharField(
        max_length=20,
        choices=[('part-time', 'Part-time'), ('volunteer', 'Volunteer'), ('full-time', 'Full-time')]
    )
    preferred_location = models.CharField(max_length=100)
    job_type_interest = models.CharField(
        max_length=20,
        choices=[('full-time', 'Full-time'), ('part-time', 'Part-time'), ('volunteer', 'Volunteer')]
    )
    skills = models.TextField(blank=True)
    location_of_interest = models.CharField(max_length=100, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='applicant_set',
        blank=True,
        help_text='The groups this applicant belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='applicant_permissions',
        blank=True,
        help_text='Specific permissions for this applicant.',
        verbose_name='user permissions'
    )

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['email', 'full_name']

    objects = ApplicantManager()

    def __str__(self):
        return f"Applicant: {self.full_name}"


class Organization(AbstractBaseUser, PermissionsMixin):
    id_number = models.CharField(max_length=50, unique=True) 
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

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
            ('Healthcare', 'Healthcare'),
            ('Education', 'Education'),
            ('Finance', 'Finance'),
            ('Retail', 'Retail'),
            ('Hospitality', 'Hospitality'),
            ('Construction', 'Construction'),
            ('Other', 'Other'),
        ]
    )
    company_type = models.CharField(
        max_length=20,
        choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')]
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='organization_set',
        blank=True,
        help_text='The groups this organization belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='organization_permissions',
        blank=True,
        help_text='Specific permissions for this organization.',
        verbose_name='user permissions'
    )

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['email', 'full_name']

    objects = OrganizationManager()

    def __str__(self):
        return f"Organization: {self.company_name}"

    
class SecurityQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class ApplicantSecurityAnswer(models.Model):
    applicant = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='security_answers')
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)


class OrganizationSecurityAnswer(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='security_answers')
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
