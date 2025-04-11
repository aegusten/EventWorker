from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from .models import User,UserSecurityAnswer, SecurityQuestion
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
import json
from django.core.exceptions import ValidationError
from django import forms
from .forms import RegisterForm
from .models import User, SecurityQuestion, UserSecurityAnswer, ApplicantProfile, OrganizationProfile

User = get_user_model()

def home_redirect_view(request):
    return redirect('login')

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            id_number = form.cleaned_data.get('id_number')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(id_number=id_number)
                user_auth = authenticate(request, username=user.username, password=password)
                if user_auth is not None:
                    login(request, user_auth)
                    return redirect('dashboard') 
                else:
                    messages.error(request, 'Invalid credentials. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'No user with that Passport ID was found.')

    return render(request, 'login.html', {'form': form})


class RegisterForm(UserCreationForm):
    question1_subquestion = forms.ChoiceField(label="Select Question 1", required=True)
    answer1 = forms.CharField(label="Answer 1", required=True)

    question2_subquestion = forms.ChoiceField(label="Select Question 2", required=True)
    answer2 = forms.CharField(label="Answer 2", required=True)

    question3_subquestion = forms.ChoiceField(label="Select Question 3 (optional)", required=False)
    answer3 = forms.CharField(label="Answer 3 (optional)", required=False)

    class Meta:
        model = User
        fields = ['id_number', 'full_name', 'phone_number', 'age', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        q1 = SecurityQuestion.objects.get(question_text="Security Question 1")
        q2 = SecurityQuestion.objects.get(question_text="Security Question 2")
        q3 = SecurityQuestion.objects.get(question_text="Security Question 3")

        self.fields['question1_subquestion'].choices = [(q1.option1, q1.option1), (q1.option2, q1.option2), (q1.option3, q1.option3)]
        self.fields['question2_subquestion'].choices = [(q2.option1, q2.option1), (q2.option2, q2.option2), (q2.option3, q2.option3)]
        self.fields['question3_subquestion'].choices = [(q3.option1, q3.option1), (q3.option2, q3.option2), (q3.option3, q3.option3)]

    def clean(self):
        cleaned = super().clean()

        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        age = cleaned.get("age")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        if age is not None and age < 18:
            self.add_error('age', "You must be at least 18 years old to register.")

        answers = [
            cleaned.get('answer1', '').strip(),
            cleaned.get('answer2', '').strip(),
            cleaned.get('answer3', '').strip()
        ]
        if sum(bool(a) for a in answers) < 2:
            raise ValidationError("Please answer at least two security questions.")

        return cleaned

@csrf_exempt
def public_verify_security_answers(request):
    try:
        data = json.loads(request.body)
        id_number = data.get('id_number', '').strip()
        user = User.objects.filter(id_number=id_number).first()

        if not user:
            return JsonResponse({'valid': False, 'error': 'User not found'}, status=404)

        user_answers = UserSecurityAnswer.objects.filter(user=user)
        correct = 0

        for ua in user_answers:
            provided_answer = data.get(str(ua.question.id), '').strip().lower()
            if provided_answer == ua.answer.strip().lower():
                correct += 1

        return JsonResponse({'valid': correct >= 2})
    except Exception:
        return JsonResponse({'valid': False, 'error': 'Server error'}, status=500)


@csrf_exempt
def validate_login_ajax(request):

    if request.method == "POST":
        data = json.loads(request.body)
        id_number = data.get("id_number")
        password = data.get("password")

        try:
            user = User.objects.get(id_number=id_number)
            if user.check_password(password):
                return JsonResponse({"valid": True})
            else:
                return JsonResponse({"valid": False, "user_exists": True, "message": "Wrong password"})
        except User.DoesNotExist:
            return JsonResponse({"valid": False, "user_exists": False, "message": "User not found"})


@csrf_exempt
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        user_type = request.POST.get("user_type", "job_seeker")

        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = user_type
            user.save()

            # Security Answers
            answers = [
                (form.cleaned_data['question1_subquestion'], form.cleaned_data['answer1']),
                (form.cleaned_data['question2_subquestion'], form.cleaned_data['answer2']),
                (form.cleaned_data['question3_subquestion'], form.cleaned_data['answer3']),
            ]
            for idx, (q_text, answer) in enumerate(answers):
                if answer.strip():
                    question_obj = SecurityQuestion.objects.all()[idx]  # assumes Q1, Q2, Q3 order
                    UserSecurityAnswer.objects.create(
                        user=user,
                        question=question_obj,
                        question_text=q_text,
                        answer=answer
                    )

            # Create related profile
            if user_type == "job_seeker":
                ApplicantProfile.objects.create(
                    user=user,
                    education=request.POST.get("education", ""),
                    availability=request.POST.get("availability", "part-time"),
                    preferred_location=request.POST.get("preferred_location", ""),
                    job_type_interest=request.POST.get("job_type_interest", ""),
                    skills=request.POST.get("skills", ""),
                    location_of_interest=request.POST.get("location_of_interest", "")
                )
            else:
                OrganizationProfile.objects.create(
                    user=user,
                    license_number=request.POST.get("license_number", ""),
                    company_name=request.POST.get("company_name", ""),
                    establishment_date=request.POST.get("establishment_date", "2000-01-01"),
                    location=request.POST.get("org_location", ""),
                    achievements=request.POST.get("achievements", ""),
                    sector=request.POST.get("sector", ""),
                    company_type=request.POST.get("company_type", "")
                )

            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id_number = data.get('id')
        new_password = data.get('newPassword')
        answers = data.get('answers')

        user = User.objects.filter(id_number=id_number).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found'})

        valid_count = 0
        for ans in answers:
            if UserSecurityAnswer.objects.filter(
                user=user,
                question_text=ans['question'],
                answer__iexact=ans['answer']
            ).exists():
                valid_count += 1

        if valid_count >= 2:
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
                "option1": q.option1,
                "option2": q.option2,
                "option3": q.option3
            })

        return JsonResponse(data, safe=False)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)
