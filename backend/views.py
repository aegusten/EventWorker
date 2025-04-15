from django.contrib.auth.backends import BaseBackend
from users.models import Applicant, Organization
from django.shortcuts import render, redirect
from users.models import JobPosting
from django.contrib.auth.decorators import login_required
from .models import Job

@login_required
def organization_dashboard(request):
    if not hasattr(request.user, 'license_number'):
        return redirect('applicant_dashboard')

    jobs = JobPosting.objects.filter(org=request.user, is_active=True)
    return render(request, 'dashboards/organization_dashboard.html', {'jobs': jobs})


@login_required
def post_new_job(request):
    # Only organization users should access this view
    if hasattr(request.user, 'user_type') and request.user.user_type != 'organization':
        return redirect('applicant_dashboard')
    if request.method == 'POST':
        # Process the form submission for a new job
        title = request.POST.get('title')
        job_type = request.POST.get('job_type')
        location = request.POST.get('location')
        deadline = request.POST.get('deadline')
        # ... (validate inputs as needed)
        # Create new Job associated with this organization user
        Job.objects.create(
            title=title, job_type=job_type, location=location, deadline=deadline,
            owner=request.user, is_active=True
        )
        # Redirect back to organization dashboard (view postings)
        return redirect('org_dashboard')
    else:
        # Render a form for creating a new job
        return render(request, 'post_new_job.html', {})
    
