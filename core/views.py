from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
import json
from django.db import models 
from django.contrib import messages
from django.http import JsonResponse
from backend.models import Message
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from backend.utils import get_chat_contacts_for_user
User = get_user_model()

from backend.models import (
    JobPosting,
    Message,
    JobApplication,
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
    context = {
        'form': form,
        'security_questions': SecurityQuestion.objects.all().order_by('id') 
    }

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
                    messages.error(request, "Unrecognized user type")
                    return redirect('login')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('login')

    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')

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
        questions = []
        applicant = Applicant.objects.filter(id_number=id_number).first()
        if applicant:
            answers = applicant.security_answers.all()
            for ans in answers:
                print("Received:", ans)
                questions.append({
                    "id": ans.question.id,
                    "question_text": ans.question_text
                })
        else:
            org = Organization.objects.filter(license_number=id_number).first()
            if org:
                answers = org.security_answers.all()
                for ans in answers:
                    questions.append({
                        "id": ans.question.id,
                        "question_text": ans.question_text
                    })
        return JsonResponse(questions, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@require_GET
def get_security_questions_choices(request):
    qs = SecurityQuestion.objects.all().order_by('id')
    data = []
    for q in qs:
        data.append([
            {"id": q.id, "text": q.option1},
            {"id": q.id, "text": q.option2},
            {"id": q.id, "text": q.option3},
        ])
    return JsonResponse(data, safe=False)

@csrf_exempt
def public_verify_security_answers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_number = data.get('id_number')
        user_type = data.get('user_type')
        answers = data.get('answers', [])

        print("Incoming ID:", id_number)
        print("User type:", user_type)
        print("Answers received from user:", answers)

        if user_type == 'applicant':
            user = Applicant.objects.filter(id_number=id_number).first()
            if not user:
                print("Applicant not found.")
                return JsonResponse({'valid': False, 'error': 'User not found'}, status=404)

            correct = 0
            print("Stored answers for applicant:")
            for a in user.security_answers.all():
                print(f"QID: {a.question.id}, Text: {a.question_text}, Answer: '{a.answer}'")

            for ans in answers:
                question_id = ans.get('question_id')
                answer = ans.get('answer', '').strip()
                print(f"Checking submitted answer: QID {question_id}, Answer: '{answer}'")
                if user.security_answers.filter(
                    question__id=question_id,
                    answer__iexact=answer
                ).exists():
                    print("✔ MATCH FOUND")
                    correct += 1
                else:
                    print(" No match")

            return JsonResponse({'valid': correct >= 2})

        elif user_type == 'organization':
            user = Organization.objects.filter(license_number=id_number).first()
            if not user:
                return JsonResponse({'valid': False, 'error': 'User not found'}, status=404)

            correct = 0
            for ans in answers:
                question = ans.get('question')
                answer = ans.get('answer', '').strip()
                if user.security_answers.filter(
                    question_text=question,
                    answer__iexact=answer
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

@csrf_exempt
@login_required
def update_security_questions(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    data = json.loads(request.body)
    questions = data.get('questions', [])

    print("Incoming security question update request")
    print("Question count:", len(questions))

    if len(questions) < 2:
        return JsonResponse({'success': False, 'message': 'At least 2 questions required'}, status=400)

    if hasattr(request.user, 'id_number'):
        user = request.user
        print("User type: Applicant")
        AnswerModel = ApplicantSecurityAnswer
        AnswerModel.objects.filter(applicant=user).delete()
    elif hasattr(request.user, 'license_number'):
        user = request.user
        print("User type: Organization")
        AnswerModel = OrganizationSecurityAnswer
        AnswerModel.objects.filter(organization=user).delete()
    else:
        print("User type: Unknown")
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    for q in questions:
        raw_value = q.get('question_id')
        answer = q.get('answer', '').strip()
        
        if not raw_value or not answer:
            continue

        try:
            question_id, question_text = raw_value.split("|", 1)
            question_obj = SecurityQuestion.objects.get(id=int(question_id))

            if hasattr(user, 'id_number'):
                AnswerModel.objects.create(
                    applicant=user,
                    question=question_obj,
                    question_text=question_text,
                    answer=answer
                )
            else:
                AnswerModel.objects.create(
                    organization=user,
                    question=question_obj,
                    question_text=question_text,
                    answer=answer
                )
        except Exception as e:
            print("Failed saving question:", raw_value, "Error:", e)
            continue


    print("Security questions update completed")
    return JsonResponse({'success': True})

@csrf_exempt
@login_required
def verify_password(request):
    if request.method != 'POST':
        return JsonResponse({'valid': False, 'message': 'Invalid method'}, status=405)

    data = json.loads(request.body)
    password = data.get('password', '').strip()

    if hasattr(request.user, 'id_number'):
        print(f"Verifying password for Applicant: {request.user.id_number}")
    elif hasattr(request.user, 'license_number'):
        print(f"Verifying password for Organization: {request.user.license_number}")
    else:
        print("Verifying password for Unknown user type")

    if request.user.check_password(password):
        return JsonResponse({'valid': True})
    return JsonResponse({'valid': False})

@csrf_exempt
@login_required
def change_password(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    user = request.user
    print("Password change request received")

    data = request.POST or json.loads(request.body)
    old_password = data.get('old_password')
    new_password1 = data.get('new_password1')
    new_password2 = data.get('new_password2')

    if not new_password1 or not new_password2:
        return JsonResponse({'success': False, 'message': 'New password fields required'}, status=400)

    if new_password1 != new_password2:
        return JsonResponse({'success': False, 'message': 'Passwords do not match'}, status=400)

    if hasattr(user, 'id_number'):
        print("User type: Applicant")
    elif hasattr(user, 'license_number'):
        print("User type: Organization")
    else:
        print("User type: Unknown")
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    if old_password:
        if not user.check_password(old_password):
            print("Old password incorrect")
            return JsonResponse({'success': False, 'message': 'Old password is incorrect'}, status=400)
    else:
        verified = data.get('verify')
        if not verified:
            print("No old password or verification")
            return JsonResponse({'success': False, 'message': 'Verification required'}, status=400)

    user.set_password(new_password1)
    user.save()

    print("Password successfully updated")
    return JsonResponse({'success': True})



def get_target_user(user_id):
    try:
        return Applicant.objects.get(pk=user_id)
    except Applicant.DoesNotExist:
        try:
            return Organization.objects.get(pk=user_id)
        except Organization.DoesNotExist:
            raise Http404("No user matches the given query.")
        
def get_user_conversations(user):
    user_ct = ContentType.objects.get_for_model(user.__class__)
    
    messages = Message.objects.filter(
        models.Q(sender_content_type=user_ct, sender_object_id=user.id) |
        models.Q(receiver_content_type=user_ct, receiver_object_id=user.id)
    ).select_related('job')

    conversation_map = {}
    
    for msg in messages:
        if msg.sender == user:
            partner = msg.receiver
        else:
            partner = msg.sender

        key = (partner, msg.job)
        if key not in conversation_map or msg.timestamp > conversation_map[key].timestamp:
            conversation_map[key] = msg

    sorted_conversations = sorted(conversation_map.items(), key=lambda x: x[1].timestamp, reverse=True)

    return sorted_conversations

@login_required
def chat_with_user_view(request, job_id, target_user_id):
    job = get_object_or_404(JobPosting, id=job_id)
    current_user = request.user
    target_user = get_target_user(target_user_id)

    if not job.is_active or not target_user.is_active:
        return render(request, 'applicant/chat.html', {
            'job': job,
            'target_user': target_user,
            'messages': [],
            'conversations': []
        })

    current_user_ct = ContentType.objects.get_for_model(current_user.__class__)
    target_user_ct = ContentType.objects.get_for_model(target_user.__class__)

    messages_qs = Message.objects.filter(
        job=job
    ).filter(
        (
            Q(sender_content_type=current_user_ct, sender_object_id=current_user.id,
              receiver_content_type=target_user_ct, receiver_object_id=target_user.id)
            |
            Q(sender_content_type=target_user_ct, sender_object_id=target_user.id,
              receiver_content_type=current_user_ct, receiver_object_id=current_user.id)
        )
    ).order_by("timestamp")

    conversations = get_user_conversations(current_user)

    if request.method == 'POST':
        content = request.POST.get("message", "").strip()
        if content:
            Message.objects.create(
                sender=current_user,
                receiver=target_user,
                job=job,
                content=content
            )
        return redirect('chat_with_user', job_id=job.id, target_user_id=target_user.id)

    context = {
        'job': job,
        'target_user': target_user,
        'messages': messages_qs,
        'conversations': conversations,
    }

    if hasattr(current_user, 'license_number'):
        return render(request, 'organization/org_chat.html', context)
    else:
        return render(request, 'applicant/main_chat.html', context)