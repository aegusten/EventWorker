from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_GET

from .forms import (
    LoginForm,
    ApplicantRegisterForm,
    OrganizationRegisterForm
)
from .models import (
    Applicant, Organization, SecurityQuestion,
    ApplicantSecurityAnswer, OrganizationSecurityAnswer
)

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
            if not user.is_active or user.account_status != 'active':
                messages.error(request, 'Your account is not active.')
                return render(request, 'login.html', context)
            if isinstance(user, Applicant):
                username_for_auth = user.id_number
            else:
                username_for_auth = user.license_number
            user_auth = authenticate(request, username=username_for_auth, password=password)
            if user_auth:
                login(request, user_auth)
                return redirect('dashboard')
            messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html', context)

def dashboard_view(request):
    return render(request, 'dashboard.html')

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
            user.is_active = True
            user.account_status = 'active'
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
            return JsonResponse({'success': True})
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

