from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Applicant, Organization
from django.contrib.auth.decorators import login_required
from backend.models import JobPosting


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_number = data.get('id','').strip()
        new_password = data.get('newPassword','').strip()
        user_type = data.get('user_type','').strip()
        answers = data.get('answers', [])
        if user_type == 'applicant':
            user = Applicant.objects.filter(id_number=id_number).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'User not found'})
            correct = 0
            for ans in answers:
                if user.security_answers.filter(
                    question_text=ans['question'],
                    answer__iexact=ans['answer']
                ).exists():
                    correct += 1
            if correct >= 2:
                user.set_password(new_password)
                user.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'message': 'Incorrect answers'})
        elif user_type == 'organization':
            user = Organization.objects.filter(license_number=id_number).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'User not found'})
            correct = 0
            for ans in answers:
                if user.security_answers.filter(
                    question_text=ans['question'],
                    answer__iexact=ans['answer']
                ).exists():
                    correct += 1
            if correct >= 2:
                user.set_password(new_password)
                user.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'message': 'Incorrect answers'})
        return JsonResponse({'success': False, 'message': 'Invalid user type'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def applicant_dashboard(request):
    if not hasattr(request.user, 'id_number'):
        return redirect('org_dashboard')

    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    jobs = JobPosting.objects.filter(is_active=True)
    if query:
        jobs = jobs.filter(title__icontains=query)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    return render(request, 'dashboards/applicant_dashboard.html', {
        'jobs': jobs,
        'search_query': query,
        'selected_job_type': job_type
    })

@login_required
def profile_view(request):
    return render(request, 'profile.html')

@login_required
def chat_view(request):
    return render(request, 'chat.html')