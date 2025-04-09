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


def register_view(request):
    return HttpResponse("Register page placeholder")