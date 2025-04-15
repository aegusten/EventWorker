from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosting  # Your job model
from .forms import JobPostingForm

def post_new_job(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.org = request.user  # Set the organization (assuming request.user is an Organization instance)
            job.save()
            return redirect('organization_dashboard')
    else:
        form = JobPostingForm()
    return render(request, 'backend/post_new_job.html', {'form': form})

def view_applicants(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    applicants = job.applications.all()  # Assuming a relation to applicants
    return render(request, 'backend/view_applicants.html', {'job': job, 'applicants': applicants})

def shortlist_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    # Add shortlisting logic here (e.g., update a status or list)
    return redirect('organization_dashboard')  # Redirect after action

def message_applicants(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    if request.method == 'POST':
        # Add messaging logic here (e.g., send email or notification)
        return redirect('organization_dashboard')
    return render(request, 'backend/message_applicants.html', {'job': job})

def delete_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    if request.method == 'POST':
        job.delete()
        return redirect('organization_dashboard')
    return render(request, 'backend/delete_job_confirm.html', {'job': job})