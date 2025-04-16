from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

import json
from .forms import LoginForm
from django.contrib import messages
from django.http import JsonResponse

from backend.models import (
    JobPosting
)

from .forms import (
    LoginForm, 
    ApplicantRegisterForm, 
    OrganizationRegisterForm
)

from users.models import (
    Applicant, 
    Organization, 
    SecurityQuestion, 
    ApplicantSecurityAnswer, 
    OrganizationSecurityAnswer
)

def home_redirect_view(request):
    return redirect('login')

def login_view(request):
    form = LoginForm(request.POST or None)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            password = form.cleaned_data['password']
            user = authenticate(request, username=id_number, password=password)
            if user:
                login(request, user) 
                if isinstance(user, Applicant):
                    return redirect('applicant_dashboard')
                elif isinstance(user, Organization):
                    return redirect('organization_dashboard')
                else:
                    messages.error(request, "Unrecognized user type.")
            else:
                messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html', context)

@login_required
def base_redirect_view(request):
    if hasattr(request.user, 'license_number'):
        return redirect('organization_dashboard')
    elif hasattr(request.user, 'id_number'):
        return redirect('applicant_dashboard')
    else:
        logout(request)
        return redirect('login')
    
@login_required
def organization_dashboard(request):
    if not hasattr(request.user, 'license_number'):
        return redirect('applicant_dashboard')
    return render(request, 'dashboards/organization_dashboard.html', {})

@login_required
def applicant_dashboard(request):
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

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'applicant':
            form = ApplicantRegisterForm(request.POST, request.FILES)
            AnswerModel = ApplicantSecurityAnswer
        elif user_type == 'organization':
            form = OrganizationRegisterForm(request.POST)
            AnswerModel = OrganizationSecurityAnswer
        else:
            return JsonResponse({'success': False, 'message': 'Invalid user type'})
        if form.is_valid():
            user = form.save(commit=False)
            user.pk = None
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.save()
            answers = [
                (form.cleaned_data['question1_subquestion'], form.cleaned_data['answer1']),
                (form.cleaned_data['question2_subquestion'], form.cleaned_data['answer2']),
                (form.cleaned_data['question3_subquestion'], form.cleaned_data['answer3'])
            ]
            questions = list(SecurityQuestion.objects.all().order_by('id'))
            for idx, (q_text, ans) in enumerate(answers):
                if ans.strip():
                    question_obj = questions[idx]
                    if user_type == 'applicant':
                        AnswerModel.objects.create(
                            applicant=user,
                            question=question_obj,
                            question_text=q_text,
                            answer=ans
                        )
                    else:
                        AnswerModel.objects.create(
                            organization=user,
                            question=question_obj,
                            question_text=q_text,
                            answer=ans
                        )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('login')
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def get_security_questions(request):
    if request.method == 'GET':
        id_number = request.GET.get('id_number', '').strip()
        if not id_number:
            return JsonResponse([], safe=False)
        applicant = Applicant.objects.filter(id_number=id_number).first()
        if applicant:
            answers = applicant.security_answers.all()
        else:
            org = Organization.objects.filter(license_number=id_number).first()
            if not org:
                return JsonResponse([], safe=False)
            answers = org.security_answers.all()
        questions = []
        for ans in answers:
            questions.append({
                "question_text": ans.question_text
            })
        return JsonResponse(questions, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_GET
def get_security_questions_choices(request):
    qs = SecurityQuestion.objects.all().order_by('id')[:3]
    data = []
    for q in qs:
        data.append({
            "question_text": q.question_text,
            "options": [q.option1, q.option2, q.option3]
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def public_verify_security_answers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_number = data.get('id_number')
        user_type = data.get('user_type')
        answers = data.get('answers', [])
        if user_type == 'applicant':
            user = Applicant.objects.filter(id_number=id_number).first()
            if not user:
                return JsonResponse({'valid': False, 'error': 'User not found'}, status=404)
            correct = 0
            for ans in answers:
                if user.security_answers.filter(
                    question_text=ans['question'],
                    answer__iexact=ans['answer']
                ).exists():
                    correct += 1
            return JsonResponse({'valid': correct >= 2})
        elif user_type == 'organization':
            user = Organization.objects.filter(license_number=id_number).first()
            if not user:
                return JsonResponse({'valid': False, 'error': 'User not found'}, status=404)
            correct = 0
            for ans in answers:
                if user.security_answers.filter(
                    question_text=ans['question'],
                    answer__iexact=ans['answer']
                ).exists():
                    correct += 1
            return JsonResponse({'valid': correct >= 2})
        return JsonResponse({'valid': False, 'error': 'Invalid user type'})
    return JsonResponse({'valid': False, 'error': 'Invalid request'}, status=400)

def check_uniqueness(request):
    id_code = request.GET.get("id_code")
    email = request.GET.get("email")
    user_type = request.GET.get("user_type")
    response = {}
    if user_type == "applicant":
        if id_code:
            exists = (Applicant.objects.filter(id_number=id_code).exists() or Organization.objects.filter(license_number=id_code).exists())
            response["id_code_exists"] = exists
        if email:
            exists = (Applicant.objects.filter(email=email).exists() or Organization.objects.filter(organization_email=email).exists())
            response["email_exists"] = exists
    elif user_type == "organization":
        if id_code:
            exists = (Organization.objects.filter(license_number=id_code).exists() or Applicant.objects.filter(id_number=id_code).exists())
            response["id_code_exists"] = exists
        if email:
            exists = (Organization.objects.filter(organization_email=email).exists() or Applicant.objects.filter(email=email).exists())
            response["email_exists"] = exists
    else:
        return JsonResponse({"error": "Invalid user type"}, status=400)
    if response:
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid request"}, status=400)

def logout_view(request):
    logout(request)
    return redirect('login')