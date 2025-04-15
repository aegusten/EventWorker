from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from backend.models import JobPosting
from users.models import Applicant, Organization
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
@csrf_exempt
def change_password(request):
    user = request.user

    if request.method == 'POST':
        if 'current_password' in request.POST:
            current_pw = request.POST['current_password']
            new_pw = request.POST['new_password']
            confirm_pw = request.POST['confirm_password']
            if not check_password(current_pw, user.password):
                messages.error(request, "Incorrect current password.")
            elif new_pw != confirm_pw:
                messages.error(request, "New passwords do not match.")
            else:
                user.set_password(new_pw)
                user.save()
                messages.success(request, "Password updated.")
        else:
            answers = []
            for i in range(1, 4):
                q = request.POST.get(f"question_{i}")
                a = request.POST.get(f"answer_{i}", "").strip()
                if q and a:
                    answers.append((q, a))

            correct = 0
            for q, a in answers:
                if user.security_answers.filter(question_text=q, answer__iexact=a).exists():
                    correct += 1

            if correct >= 2:
                new_pw = request.POST['new_password']
                confirm_pw = request.POST['confirm_password']
                if new_pw != confirm_pw:
                    messages.error(request, "Passwords do not match.")
                else:
                    user.set_password(new_pw)
                    user.save()
                    messages.success(request, "Password updated.")
            else:
                messages.error(request, "Security answers did not match.")

        return redirect('profile_view')

@login_required
def verify_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        current_pw = data.get("password")
        if current_pw and request.user.check_password(current_pw):
            request.session['password_verification_passed'] = True
            return JsonResponse({"valid": True})
        return JsonResponse({"valid": False})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def verify_security_answers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        answers = data.get('answers', [])
        user = request.user
        correct = 0
        for ans in answers:
            if user.security_answers.filter(
                question_text=ans['question'],
                answer__iexact=ans['answer'].strip()
            ).exists():
                correct += 1
        if correct >= 2:
            request.session['password_verification_passed'] = True
            return JsonResponse({'valid': True})
        return JsonResponse({'valid': False})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        if request.session.get('password_verification_passed', False):
            new_pw = request.POST.get('new_password1')
            confirm_pw = request.POST.get('new_password2')
            if new_pw != confirm_pw:
                messages.error(request, "New passwords do not match.")
            else:
                request.user.set_password(new_pw)
                request.user.save()
                del request.session['password_verification_passed']
                messages.success(request, "Password updated successfully.")
            return redirect('profile_view')
        else:
            messages.error(request, "Verification failed.")
            return redirect('profile_view')
    return render(request, 'profile.html')

@login_required
def change_security_phrase(request):
    return render(request, 'applicant/change_security.html')

# --- PROFILE VIEW (Applicant) ---
@login_required
def profile_view(request):
    applicant = request.user

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone_number').strip()
        country = request.POST.get('country').strip()
        address = request.POST.get('address').strip()
        skills = request.POST.get('skills').strip()
        preferred_location = request.POST.get('preferred_location').strip()
        availability = request.POST.get('availability')
        interest = request.POST.get('job_type_interest')
        cv_file = request.FILES.get('cv')

        # Email validation
        email_taken = Applicant.objects.exclude(pk=applicant.pk).filter(email=email).exists() or \
                      Organization.objects.filter(organization_email=email).exists()
        if email_taken:
            messages.error(request, "This email is already taken by another account.")
        else:
            # Save changes
            applicant.email = email
            applicant.phone_number = phone
            applicant.country = country
            applicant.address = address
            applicant.skills = skills
            applicant.preferred_location = preferred_location
            applicant.availability = availability
            applicant.job_type_interest = interest
            if cv_file:
                applicant.cv = cv_file
            applicant.save()
            messages.success(request, "Profile updated successfully.")

        return redirect('profile_view') 

    return render(request, 'applicant/profile.html', {'applicant': applicant})


# --- CHAT VIEW ---
@login_required
def chat_view(request):
    return render(request, 'chat.html')

@login_required
def search_jobs(request):
    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    
    jobs = JobPosting.objects.filter(is_active=True)
    
    if query:
        jobs = jobs.filter(title__icontains=query)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    return render(request, 'applicant/search.html', {
        'jobs': jobs,
        'search_query': query,
        'selected_job_type': job_type
    })
