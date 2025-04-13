from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Applicant, Organization, SecurityQuestion

class LoginForm(forms.Form):
    id_number = forms.CharField(label="Passport/License ID", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ApplicantRegisterForm(UserCreationForm):
    question1_subquestion = forms.ChoiceField(label="Select Question 1", required=True)
    answer1 = forms.CharField(label="Answer 1", required=True)
    question2_subquestion = forms.ChoiceField(label="Select Question 2", required=True)
    answer2 = forms.CharField(label="Answer 2", required=True)
    question3_subquestion = forms.ChoiceField(label="Select Question 3 (optional)", required=False)
    answer3 = forms.CharField(label="Answer 3 (optional)", required=False)

    class Meta:
        model = Applicant
        fields = [
            'id_number','full_name','email','phone_number','age','country','address',
            'education','cv','availability','preferred_location','job_type_interest',
            'skills','location_of_interest','password1','password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = list(SecurityQuestion.objects.all().order_by('id'))
        if len(questions) >= 3:
            q1, q2, q3 = questions[:3]
            self.fields['question1_subquestion'].choices = [
                (q1.option1, q1.option1),
                (q1.option2, q1.option2),
                (q1.option3, q1.option3)
            ]
            self.fields['question2_subquestion'].choices = [
                (q2.option1, q2.option1),
                (q2.option2, q2.option2),
                (q2.option3, q2.option3)
            ]
            self.fields['question3_subquestion'].choices = [
                (q3.option1, q3.option1),
                (q3.option2, q3.option2),
                (q3.option3, q3.option3)
            ]

    def clean_age(self):
        age_val = self.cleaned_data.get('age')
        availability_val = self.cleaned_data.get('availability','').strip()
        if availability_val == 'full-time' and age_val < 18:
            raise ValidationError("You must be at least 18 for a full-time position.")
        if availability_val != 'full-time' and age_val < 14:
            raise ValidationError("You must be at least 14 for part-time or volunteer.")
        if age_val > 100:
            raise ValidationError("Age cannot exceed 100.")
        return age_val

    def clean(self):
        cleaned = super().clean()
        answers = [
            cleaned.get('answer1','').strip(),
            cleaned.get('answer2','').strip(),
            cleaned.get('answer3','').strip()
        ]
        if sum(bool(a) for a in answers) < 2:
            raise forms.ValidationError("Please answer at least two security questions.")
        return cleaned

class OrganizationRegisterForm(UserCreationForm):
    question1_subquestion = forms.ChoiceField(label="Select Question 1", required=True)
    answer1 = forms.CharField(label="Answer 1", required=True)
    question2_subquestion = forms.ChoiceField(label="Select Question 2", required=True)
    answer2 = forms.CharField(label="Answer 2", required=True)
    question3_subquestion = forms.ChoiceField(label="Select Question 3 (optional)", required=False)
    answer3 = forms.CharField(label="Answer 3 (optional)", required=False)

    class Meta:
        model = Organization
        fields = [
            'license_number','organization_name','organization_email','organization_phone',
            'establishment_date','location','achievements','sector','company_type',
            'password1','password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = list(SecurityQuestion.objects.all().order_by('id'))
        if len(questions) >= 3:
            q1, q2, q3 = questions[:3]
            self.fields['question1_subquestion'].choices = [
                (q1.option1, q1.option1),
                (q1.option2, q1.option2),
                (q1.option3, q1.option3)
            ]
            self.fields['question2_subquestion'].choices = [
                (q2.option1, q2.option1),
                (q2.option2, q2.option2),
                (q2.option3, q2.option3)
            ]
            self.fields['question3_subquestion'].choices = [
                (q3.option1, q3.option1),
                (q3.option2, q3.option2),
                (q3.option3, q3.option3)
            ]

    def clean(self):
        cleaned = super().clean()
        answers = [
            cleaned.get('answer1','').strip(),
            cleaned.get('answer2','').strip(),
            cleaned.get('answer3','').strip()
        ]
        if sum(bool(a) for a in answers) < 2:
            raise forms.ValidationError("Please answer at least two security questions.")
        return cleaned
