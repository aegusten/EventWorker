from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobPosting
from .forms import JobPostingForm

# Organization Dashboard View
@login_required
def organization_dashboard(request):
    jobs = JobPosting.objects.filter(org=request.user)

    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.org = request.user
            job.save()
            return redirect('organization_dashboard')
    else:
        form = JobPostingForm()

    return render(request, 'dashboards/organization_dashboard.html', {
        'jobs': jobs,
        'form': form
    })


# Organization Profile Page
@login_required
def organization_profile_view(request):
    org = request.user
    if request.method == 'POST':
        org.company_name = request.POST.get('company_name')
        org.license_number = request.POST.get('license_number')
        org.location = request.POST.get('location')
        org.established = request.POST.get('established')
        org.company_type = request.POST.get('company_type')
        org.working_sector = request.POST.get('working_sector')
        org.achievements = request.POST.get('achievements')
        org.security_phrase = request.POST.get('security_phrase')
        new_password = request.POST.get('password')

        if new_password:
            org.set_password(new_password)

        org.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('organization_profile_view')

    return render(request, 'organization/organization_profile.html', {'organization': org})


# View Applicants for a Specific Job
@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    applicants = job.applications.all()  # Assuming `applications` is related name
    return render(request, 'backend/view_applicants.html', {'job': job, 'applicants': applicants})

# Shortlist a Job (dummy logic placeholder)
@login_required
def shortlist_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    # Add actual shortlisting logic if needed
    return redirect('organization_dashboard')

# Send Message to Applicants
@login_required
def message_applicants(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    if request.method == 'POST':
        # Placeholder for messaging logic
        return redirect('organization_dashboard')
    return render(request, 'backend/message_applicants.html', {'job': job})

# Delete a Job
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, organization=request.user)
    if request.method == 'POST':
        job.delete()
        return redirect('organization_dashboard')
    return render(request, 'backend/delete_job_confirm.html', {'job': job})

# Chat View (generic for now)
@login_required
def chat_view(request):
    return render(request, 'dashboards/org_chat.html')
