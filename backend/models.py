from django.db import models
from django.utils import timezone
from django.conf import settings
from users.models import Applicant, Organization
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class JobPosting(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('volunteer', 'Volunteer')
    ])
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    requirements = models.TextField()
    deadline = models.DateField()
    description = models.TextField()
    image = models.ImageField(upload_to='static/jobs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.org.organization_name}"


class JobApplication(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')  
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    message_to_org = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    application_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Application {self.application_id} by {self.applicant.id_number}"


class Message(models.Model):
    sender_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True
    )
    sender_object_id = models.PositiveIntegerField(null=True)
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')

    receiver_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True
    )
    receiver_object_id = models.PositiveIntegerField(null=True)
    receiver = GenericForeignKey('receiver_content_type', 'receiver_object_id')

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        sender_id = getattr(self.sender, 'id_number', getattr(self.sender, 'license_number', 'UnknownSender'))
        receiver_id = getattr(self.receiver, 'id_number', getattr(self.receiver, 'license_number', 'UnknownReceiver'))
        return f"Message from {sender_id} to {receiver_id}"



class Feedback(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Feedback for {self.job.title} by {self.applicant.id_number}"
