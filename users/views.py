from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

import json

from .forms import (
    LoginForm,
    ApplicantRegisterForm,
    OrganizationRegisterForm
)

from .models import (
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
        
    if request.method == 'POST':
        if form.is_valid():
            id_number = form.cleaned_data.get('id_number')
            password = form.cleaned_data.get('password')

            try:
                user = Applicant.objects.get(id_number=id_number)
            except Applicant.DoesNotExist:
                try:
                    user = Organization.objects.get(id_number=id_number)
                except Organization.DoesNotExist:
                    messages.error(request, 'No user with that Passport ID was found.')
                    return render(request, 'login.html', {'form': form})

            user_auth = authenticate(request, username=user.id_number, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return redirect('dashboard') 
            else:
                messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'login.html', {'form': form})

@csrf_exempt
def validate_login_ajax(request):
    pass
    # if request.method == "POST":
    #     data = json.loads(request.body)
    #     id_number = data.get("id_number")
    #     password = data.get("password")

    #     try:
    #         user = User.objects.get(id_number=id_number)
    #         if user.check_password(password):
    #             return JsonResponse({"valid": True})
    #         else:
    #             return JsonResponse({"valid": False, "user_exists": True, "message": "Wrong password"})
    #     except User.DoesNotExist:
    #         return JsonResponse({"valid": False, "user_exists": False, "message": "User not found"})
        
@csrf_exempt
def register_view(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        if user_type == "applicant":
            form = ApplicantRegisterForm(request.POST, request.FILES)
            AnswerModel = ApplicantSecurityAnswer
            UserModel = Applicant
        elif user_type == "organization":
            form = OrganizationRegisterForm(request.POST)
            AnswerModel = OrganizationSecurityAnswer
            UserModel = Organization
        else:
            return JsonResponse({"success": False, "message": "Invalid user type"})

        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            answers = [
                (form.cleaned_data["question1_subquestion"], form.cleaned_data["answer1"]),
                (form.cleaned_data["question2_subquestion"], form.cleaned_data["answer2"]),
                (form.cleaned_data["question3_subquestion"], form.cleaned_data["answer3"]),
            ]

            questions = list(SecurityQuestion.objects.all().order_by("id"))
            for idx, (q_text, ans) in enumerate(answers):
                if ans.strip():
                    question_obj = questions[idx] 
                    AnswerModel.objects.create(
                        **{user_type: user},
                        question=question_obj,
                        question_text=q_text,
                        answer=ans
                    )

            login(request, user)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id_number = data.get('id')
        new_password = data.get('newPassword')
        answers = data.get('answers')
        user_type = data.get('user_type')

        if user_type == 'applicant':
            from .models import Applicant as UserModel, ApplicantSecurityAnswer as AnswerModel
        elif user_type == 'organization':
            from .models import Organization as UserModel, OrganizationSecurityAnswer as AnswerModel
        else:
            return JsonResponse({'success': False, 'message': 'Invalid user type'})

        user = UserModel.objects.filter(id_number=id_number).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found'})

        correct = 0
        for ans in answers:
            if AnswerModel.objects.filter(
                **{user_type: user},
                question_text=ans['question'],
                answer__iexact=ans['answer']
            ).exists():
                correct += 1

        if correct >= 2:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Incorrect answers'})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@csrf_exempt
def get_security_questions(request):
    if request.method == "GET":
        questions = SecurityQuestion.objects.all()
        data = []

        for q in questions:
            data.append({
                "id": q.id,
                "question_text": q.question_text,
                "options": [q.option1, q.option2, q.option3]
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def public_verify_security_answers(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id_number = data.get('id_number')
        user_type = data.get('user_type')
        answers = data.get('answers')

        if user_type == 'applicant':
            from .models import Applicant as UserModel, ApplicantSecurityAnswer as AnswerModel
        elif user_type == 'organization':
            from .models import Organization as UserModel, OrganizationSecurityAnswer as AnswerModel
        else:
            return JsonResponse({'valid': False, 'error': 'Invalid user type'})

        user = UserModel.objects.filter(id_number=id_number).first()
        if not user:
            return JsonResponse({'valid': False, 'error': 'User not found'}, status=404)

        correct = 0
        for ans in answers:
            if AnswerModel.objects.filter(
                **{user_type: user},
                question_text=ans["question"],
                answer__iexact=ans["answer"]
            ).exists():
                correct += 1

        return JsonResponse({'valid': correct >= 2})

    return JsonResponse({'valid': False, 'error': 'Invalid request'}, status=400)
