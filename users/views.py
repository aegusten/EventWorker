from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from backend.models import JobPosting
from users.models import Applicant, Organization
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def profile_view(request):
    applicant = request.user

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone_number').strip()
        country = request.POST.get('country').strip()
        address = request.POST.get('address').strip()
        skills = request.POST.get('skills').strip()
        preferred_location = request.POST.get('preferred_location').strip()
        availability = request.POST.get('availability')
        interest = request.POST.get('job_type_interest')
        cv_file = request.FILES.get('cv')

        # Email validation
        email_taken = Applicant.objects.exclude(pk=applicant.pk).filter(email=email).exists() or \
                      Organization.objects.filter(organization_email=email).exists()
        if email_taken:
            messages.error(request, "This email is already taken by another account.")
        else:
            # Save changes
            applicant.email = email
            applicant.phone_number = phone
            applicant.country = country
            applicant.address = address
            applicant.skills = skills
            applicant.preferred_location = preferred_location
            applicant.availability = availability
            applicant.job_type_interest = interest
            if cv_file:
                applicant.cv = cv_file
            applicant.save()
            messages.success(request, "Profile updated successfully.")

        return redirect('profile_view') 

    return render(request, 'applicant/profile.html', {'applicant': applicant})


# --- CHAT VIEW ---
@login_required
def chat_view(request):
    return render(request, 'chat.html')

@login_required
def search_jobs(request):
    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    
    jobs = JobPosting.objects.filter(is_active=True)
    
    if query:
        jobs = jobs.filter(title__icontains=query)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    return render(request, 'applicant/search.html', {
        'jobs': jobs,
        'search_query': query,
        'selected_job_type': job_type
    })
