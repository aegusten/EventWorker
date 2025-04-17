from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobPosting, JobApplication
from .forms import JobPostingForm
from users.models import Organization
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@login_required
def organization_dashboard(request):
    print(" POST received:", request.POST)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.org = request.user
            job.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                data = {
                    'id': job.id,
                    'title': job.title,
                    'job_type': job.job_type,
                    'location': job.location,
                    'deadline': str(job.deadline),
                }
                return JsonResponse({'success': True, 'job': data})

            return redirect('organization_dashboard')  

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    jobs = JobPosting.objects.filter(org=request.user, is_active=True)
    form = JobPostingForm()
    return render(request, 'dashboards/organization_dashboard.html', {
        'jobs': jobs,
        'form': form
    })

@login_required
def organization_profile_view(request):
    org = request.user

    if request.method == 'POST':
        org.organization_name = request.POST.get('organization_name')
        org.license_number = request.POST.get('license_number')
        org.organization_email = request.POST.get('organization_email')
        org.organization_phone = request.POST.get('organization_phone')
        org.location = request.POST.get('location')
        org.establishment_date = request.POST.get('establishment_date')
        org.company_type = request.POST.get('company_type')
        org.sector = request.POST.get('sector')
        org.achievements = request.POST.get('achievements')
        org.security_phrase = request.POST.get('security_phrase')

        new_password = request.POST.get('password')
        if new_password:
            org.set_password(new_password)

        org.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('organization_profile_view')

    context = {
        'organization': org,
        'sector_choices': Organization._meta.get_field('sector').choices,
        'company_type_choices': Organization._meta.get_field('company_type').choices
    }
    return render(request, 'organization/organization_profile.html', context)

@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, org=request.user)
    applicants = job.applications.all()
    return render(request, 'organization/view_applicants.html', {
        'job': job,
        'applicants': applicants
    })

@login_required
def message_applicants(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, org=request.user)
    if request.method == 'POST':
        return redirect('organization_dashboard')
    return render(request, 'backend/message_applicants.html', {'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, org=request.user)
    if request.method == 'POST':
        job.is_active = False
        job.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('organization_dashboard')

    return render(request, 'backend/delete_job_confirm.html', {'job': job})

@login_required
def chat_view(request):
    return render(request, 'organization/org_chat.html')

@login_required
@require_GET
def get_allowed_job_types(request):
    org = request.user
    job_type_map = {
        'small': ['volunteer'],
        'medium': ['part-time', 'volunteer'],
        'large': ['full-time', 'part-time', 'volunteer'],
    }
    
    allowed = job_type_map.get(org.company_type.lower(), [])

    print(f"[DEBUG] Org: {org.organization_name}, Type: {org.company_type}, Allowed Job Types: {allowed}")

    return JsonResponse({'allowed_types': allowed})


@login_required
def accept_applicant(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = 'accepted'
    application.save()
    messages.success(request, "Applicant accepted successfully.")
    return redirect('view_applicants', job_id=application.job.id)

@login_required
def reject_applicant(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = 'rejected'
    application.save()
    messages.success(request, "Applicant rejected successfully.")
    return redirect('view_applicants', job_id=application.job.id)