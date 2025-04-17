from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from backend.models import JobPosting
from users.models import Applicant, Organization
from django.http import JsonResponse
from django.utils import timezone
import uuid
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from backend.models import JobPosting, JobApplication
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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

        email_taken = Applicant.objects.exclude(pk=applicant.pk).filter(email=email).exists() or \
                      Organization.objects.filter(organization_email=email).exists()
        if email_taken:
            messages.error(request, "This email is already taken by another account.")
        else:
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

@login_required
def applicant_catalog_view(request):
    user = request.user
    applied_job_ids = JobApplication.objects.filter(applicant=user).values_list('job_id', flat=True)

    un_applied_jobs = JobPosting.objects.filter(is_active=True).exclude(id__in=applied_job_ids).order_by('-created_at')[:6]

    return render(request, 'applicant/catalog.html', {
        'jobs': un_applied_jobs,
    })
    
@login_required
def applicant_dashboard(request):
    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    page_number = request.GET.get('page', 1)
    
    applicant = request.user

    jobs = JobPosting.objects.filter(is_active=True)

    if query:
        jobs = jobs.filter(title__icontains=query)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    applied_jobs = JobApplication.objects.filter(applicant=applicant).values_list('job_id', flat=True)
    jobs = jobs.exclude(id__in=applied_jobs)

    has_visible_jobs = jobs.exists()

    paginator = Paginator(jobs, 6)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'applied_job_ids': applied_jobs,
        'query': query,
        'job_type': job_type,
        'has_visible_jobs': has_visible_jobs,
        'jobs': jobs,
    }
    return render(request, 'dashboards/applicant_dashboard.html', context)

@require_POST
@login_required
def apply_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)

    applicant = request.user
    
    try:
        applicant = Applicant.objects.get(pk=request.user.pk)
    except Applicant.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Only applicants can apply.'}, status=403)

    if JobApplication.objects.filter(applicant=applicant, job=job).exists():
        return JsonResponse({'success': False, 'message': 'You have already applied to this job.'}, status=400)

    application_id = f"APP-{uuid.uuid4().hex[:10].upper()}"

    JobApplication.objects.create(
        applicant=applicant,
        job=job,
        application_id=application_id
    )

    return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})

@login_required
def recently_applied_view(request):
    applicant = request.user
    applications = JobApplication.objects.select_related('job').filter(
        applicant=applicant,
        job__is_active=True
    )
    paginator = Paginator(applications, 6)  
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number) 
    return render(request, 'applicant/recently_applied.html', {
        'page_obj': page_obj, 
    })
    
@login_required
def submit_feedback(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id, applicant=request.user)

    if application.status != "accepted":
        messages.error(request, "You can only give feedback for accepted jobs.")
        return redirect("recently_applied")

    if application.feedback:
        messages.warning(request, "Feedback already submitted.")
        return redirect("recently_applied")

    if request.method == "POST":
        feedback = request.POST.get("feedback", "").strip()
        if feedback:
            application.feedback = feedback
            application.save()
            messages.success(request, "Feedback submitted successfully.")
        else:
            messages.warning(request, "Feedback cannot be empty.")

    return redirect("recently_applied")

@login_required
def chat_view(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)

    return render(request, 'applicant/chat.html', {
        'job': job
    })