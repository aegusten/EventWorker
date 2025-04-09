from django.db import models
from users.models import ApplicantProfile, OrganizationProfile
from django.conf import settings
from django.utils import timezone

class JobPosting(models.Model):
    org = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=[('full-time', 'Full-time'), ('part-time', 'Part-time'), ('volunteer', 'Volunteer')])
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    requirements = models.TextField()
    deadline = models.DateField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.org.company_name}"


class JobApplication(models.Model):
    applicant = models.ForeignKey('users.ApplicantProfile', on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    message_to_org = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    application_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Application {self.application_id} by {self.applicant.user.id_number}"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.id_number} to {self.receiver.id_number}"


class Feedback(models.Model):
    applicant = models.ForeignKey(ApplicantProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.job.title} by {self.applicant.user.id_number}"
