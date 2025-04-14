from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_GET
from .forms import LoginForm, ApplicantRegisterForm, OrganizationRegisterForm
from .models import Applicant, Organization, SecurityQuestion, ApplicantSecurityAnswer, OrganizationSecurityAnswer
from django.contrib.auth.decorators import login_required
from backend.models import JobPosting
from .forms import LoginForm
from django.contrib.auth import logout

def home_redirect_view(request):
    return redirect('login')

def login_view(request):
    form = LoginForm(request.POST if request.method == 'POST' else None)
    security_questions = SecurityQuestion.objects.all().order_by('id')[:3]
    context = {
        'form': form,
        'security_questions': security_questions,
    }
    if request.method == 'POST':
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            password = form.cleaned_data['password']
            user = None
            try:
                user = Applicant.objects.get(id_number=id_number)
            except Applicant.DoesNotExist:
                try:
                    user = Organization.objects.get(license_number=id_number)
                except Organization.DoesNotExist:
                    messages.error(request, 'No user with that ID was found.')
                    return render(request, 'login.html', context)
            if not user.is_active:
                messages.error(request, 'Your account is not active.')
                return render(request, 'login.html', context)
            if isinstance(user, Applicant):
                username_for_auth = user.id_number
            else:
                username_for_auth = user.license_number
            user_auth = authenticate(request, username=username_for_auth, password=password)
            if user_auth:
                login(request, user_auth)
                return redirect('base')
            messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html', context)

@login_required
def base_redirect_view(request):
    return render(request, 'base.html')

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
            user.set_password(form.cleaned_data['password']) 
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
            login(request, user)
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
    

@login_required
def profile_view(request):
    return render(request, 'profile.html')

@login_required
def chat_view(request):
    return render(request, 'chat.html')

def logout_view(request):
    logout(request)
    return redirect('login')