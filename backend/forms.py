from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'job_type', 'salary', 'location', 'requirements', 'deadline', 'description', 'image']
