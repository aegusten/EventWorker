# EventWork Connect

EventWork Connect is a web-based job matchmaking platform built to streamline the connection between **job seekers (applicants)** and **job providers (organizations)** in Malaysia. The system supports full-time, part-time, and volunteer opportunities with a secure and user-friendly interface.

---

## 🔧 Features

### 🧑 Applicant Module
- Secure registration with Passport ID & password
- Multi-step registration form with education, CV upload, location & job preferences
- Security questions for password recovery
- Dashboard access upon login

### 🏢 Organization Module
- Registration with license and business details
- Profile setup: sector, size, location, achievements
- Security questions for recovery
- Job post features (coming soon)

### 🔐 Authentication
- Login with Passport ID & password
- CSRF-protected sessions
- Password reset via security questions
- Backend validation for:
  - Matching passwords
  - Age (must be over 18)
  - Required security answers

---

## 🚀 Tech Stack

- **Backend**: Django (v4.2+), PostgreSQL
- **Frontend**: HTML + Bootstrap 5 + JavaScript
- **Styling**: Custom CSS, Bootstrap components
- **Auth**: Django's `AbstractBaseUser`, custom `User` model
- **Security**: Password hashing, CSRF, validation logic
- **Forms**: Django crispy forms with Bootstrap 5 theme
- **Other Tools**: Celery (future tasks), Redis (future sessions/cache)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/eventwork-connect.git
cd eventwork-connect
