from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobPosting
from .forms import JobPostingForm
from users.models import Organization
from django.http import JsonResponse

@login_required
def organization_dashboard(request):
    print("🔔 POST received:", request.POST)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.org = request.user
            job.save()

            # CHECK IF AJAX (so JSON only if using fetch)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                data = {
                    'id': job.id,
                    'title': job.title,
                    'job_type': job.job_type,
                    'location': job.location,
                    'deadline': str(job.deadline),
                }
                return JsonResponse({'success': True, 'job': data})

            return redirect('organization_dashboard')  # fallback

        # Handle form invalid JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # GET method
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
        org.license_number = request.POST.get('license_number')  # optional
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
def shortlist_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, org=request.user)
    return redirect('organization_dashboard')

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

        # Handle AJAX deletion
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('organization_dashboard')

    return render(request, 'backend/delete_job_confirm.html', {'job': job})

@login_required
def chat_view(request):
    return render(request, 'dashboards/org_chat.html')
