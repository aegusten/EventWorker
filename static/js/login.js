document.addEventListener("DOMContentLoaded", function() {
  // DOM elements (unchanged from your code)
  var applicantIcon = document.getElementById("applicantIcon");
  var organizationIcon = document.getElementById("organizationIcon");
  var userTypeInput = document.getElementById("user_type");
  var applicantOnly = document.querySelectorAll(".applicant-only");
  var orgOnly = document.querySelectorAll(".org-only");
  var step1 = document.getElementById("signupStep1");
  var step2 = document.getElementById("signupStep2");
  var signupNextBtn = document.getElementById("signupNextBtn");
  var signupBackBtn = document.getElementById("signupBackBtn");
  var signupForm = document.getElementById("signupForm");
  var password1 = document.querySelector('input[name="password1"]');
  var password2 = document.querySelector('input[name="password2"]');
  var ageInput = document.querySelector('input[name="age"]');
  var availabilitySelect = document.querySelector('select[name="availability"]');
  var jobTypeSelect = document.querySelector('select[name="job_type_interest"]');
  var passwordError = document.createElement("div");
  var ageError = document.createElement("div");

  // Email and ID code validation elements
  var applicantEmailInput = document.querySelector('.applicant-only input[name="email"]');
  var orgEmailInput = document.querySelector('.org-only input[name="organization_email"]');
  var applicantIdInput = document.querySelector('.applicant-only input[name="id_number"]');
  var orgIdInput = document.querySelector('.org-only input[name="license_number"]');
  var applicantEmailError = document.querySelector('.applicant-only .email-error');
  var orgEmailError = document.querySelector('.org-only .email-error');
  var applicantIdError = document.querySelector('.applicant-only .id-code-error');
  var orgIdError = document.querySelector('.org-only .id-code-error');

  // Setup error message elements (unchanged)
  passwordError.className = "text-danger mt-1";
  password2.parentElement.appendChild(passwordError);

  ageError.className = "text-danger mt-1";
  jobTypeSelect.parentElement.appendChild(ageError);

  // Password and age validation functions (unchanged)
  function validatePasswords() {
    if (password1.value && password2.value) {
      if (password1.value !== password2.value) {
        passwordError.textContent = "Passwords do not match.";
        signupNextBtn.disabled = true;
      } else {
        passwordError.textContent = "";
        signupNextBtn.disabled = false;
      }
    } else {
      passwordError.textContent = "";
      signupNextBtn.disabled = false;
    }
  }

  function validateAge() {
    var age = parseInt(ageInput.value, 10) || 0;
    var availability = availabilitySelect.value;
    var jobType = jobTypeSelect.value;
    var submitButton = signupForm.querySelector('button[type="submit"]');

    if (age > 100) {
      ageError.textContent = "Age cannot exceed 100.";
      submitButton.disabled = true;
    } else if (jobType === "full-time" || availability === "full-time") {
      if (age < 14) {
        ageError.textContent = "You must be at least 14 to register for a full-time job.";
        submitButton.disabled = true;
      } else if (age < 18) {
        ageError.textContent = "You must be at least 18 to register for a full-time job.";
        submitButton.disabled = true;
      } else {
        ageError.textContent = "";
        submitButton.disabled = false;
      }
    } else {
      ageError.textContent = "";
      submitButton.disabled = false;
    }
  }

  // Get current inputs based on user type (unchanged)
  function getCurrentInputs() {
    var userType = userTypeInput.value;
    if (userType === 'applicant') {
      return {
        emailInput: applicantEmailInput,
        idInput: applicantIdInput,
        emailError: applicantEmailError,
        idError: applicantIdError
      };
    } else {
      return {
        emailInput: orgEmailInput,
        idInput: orgIdInput,
        emailError: orgEmailError,
        idError: orgIdError
      };
    }
  }

  // Check email uniqueness
  function checkEmail() {
    var inputs = getCurrentInputs();
    var email = inputs.emailInput.value.trim();
    var userType = userTypeInput.value;
    if (email) {
      fetch('/account/check_uniqueness/?email=' + encodeURIComponent(email) + '&user_type=' + userType)
        .then(response => {
          if (!response.ok) {
            throw new Error('Server error');
          }
          return response.json();
        })
        .then(data => {
          if (data.email_exists) {
            inputs.emailError.textContent = 'This email is already taken.';
          } else {
            inputs.emailError.textContent = '';
          }
        })
        .catch(() => {
          inputs.emailError.textContent = 'Error checking email.';
        });
    } else {
      inputs.emailError.textContent = '';
    }
  }

  function checkIdCode() {
    var inputs = getCurrentInputs();
    var idCode = inputs.idInput.value.trim();
    var userType = userTypeInput.value;
    if (idCode) {
      fetch('/account/check_uniqueness/?id_code=' + encodeURIComponent(idCode) + '&user_type=' + userType)
        .then(response => {
          if (!response.ok) {
            throw new Error('Server error');
          }
          return response.json();
        })
        .then(data => {
          if (data.id_code_exists) {
            inputs.idError.textContent = 'This ID code is already taken.';
          } else {
            inputs.idError.textContent = '';
          }
        })
        .catch(() => {
          inputs.idError.textContent = 'Error checking ID code.';
        });
    } else {
      inputs.idError.textContent = '';
    }
  }
  

  // Event listeners (unchanged)
  applicantEmailInput.addEventListener('blur', checkEmail);
  orgEmailInput.addEventListener('blur', checkEmail);
  applicantIdInput.addEventListener('blur', checkIdCode);
  orgIdInput.addEventListener('blur', checkIdCode);

  password1.addEventListener("input", validatePasswords);
  password2.addEventListener("input", validatePasswords);
  ageInput.addEventListener("input", validateAge);
  availabilitySelect.addEventListener("change", validateAge);
  jobTypeSelect.addEventListener("change", validateAge);

  // Applicant and Organization icon click handlers (unchanged)
  if (applicantIcon) {
    applicantIcon.onclick = function() {
      userTypeInput.value = "applicant";
      applicantIcon.classList.add("active-type");
      organizationIcon.classList.remove("active-type");
      applicantOnly.forEach(function(el) { el.classList.remove("d-none"); });
      orgOnly.forEach(function(el) { el.classList.add("d-none"); });
      applicantEmailError.textContent = '';
      applicantIdError.textContent = '';
      orgEmailError.textContent = '';
      orgIdError.textContent = '';
    };
  }

  if (organizationIcon) {
    organizationIcon.onclick = function() {
      userTypeInput.value = "organization";
      organizationIcon.classList.add("active-type");
      applicantIcon.classList.remove("active-type");
      orgOnly.forEach(function(el) { el.classList.remove("d-none"); });
      applicantOnly.forEach(function(el) { el.classList.add("d-none"); });
      applicantEmailError.textContent = '';
      applicantIdError.textContent = '';
      orgEmailError.textContent = '';
      orgIdError.textContent = '';
    };
  }

  // Step 1 validation and navigation (unchanged)
  function validateStep1() {
    var inputs = getCurrentInputs();
    var email = inputs.emailInput.value.trim();
    var idCode = inputs.idInput.value.trim();
    var password1Val = password1.value.trim();
    var password2Val = password2.value.trim();

    if (!email || !idCode || !password1Val || !password2Val) {
      alert('Please fill all required fields in step 1.');
      return false;
    }

    if (password1Val !== password2Val) {
      passwordError.textContent = "Passwords do not match.";
      return false;
    }

    if (inputs.emailError.textContent || inputs.idError.textContent) {
      alert('Please correct the errors before proceeding.');
      return false;
    }

    return true;
  }

  if (signupNextBtn) {
    signupNextBtn.onclick = function() {
      if (validateStep1()) {
        step1.classList.add("d-none");
        step2.classList.remove("d-none");
        if (userTypeInput.value === "applicant") {
          applicantOnly.forEach(function(el) { el.classList.remove("d-none"); });
        } else {
          orgOnly.forEach(function(el) { el.classList.remove("d-none"); });
        }
        document.getElementById("userTypeIcons").classList.add("d-none");
      }
    };
  }

  if (signupBackBtn) {
    signupBackBtn.onclick = function() {
      step2.classList.add("d-none");
      step1.classList.remove("d-none");
      document.getElementById("userTypeIcons").classList.remove("d-none");
      if (userTypeInput.value === "applicant") {
        orgOnly.forEach(function(el) { el.classList.add("d-none"); });
      } else {
        applicantOnly.forEach(function(el) { el.classList.add("d-none"); });
      }
    };
  }

  // Forgot password logic (unchanged, included for completeness)
  var forgotId = document.getElementById("forgotId");
  var forgotUserType = document.getElementById("forgotUserType");
  var securityQuestions = document.getElementById("securityQuestions");
  var newPwFields = document.getElementById("newPwFields");
  var forgotError = document.getElementById("forgotError");
  var verifyBtn = document.getElementById("verifyBtn");
  var answeredQuestions = false;

  if (verifyBtn) {
    verifyBtn.onclick = function() {
      if (!answeredQuestions) {
        securityQuestions.innerHTML = "";
        securityQuestions.classList.add("d-none");
        newPwFields.classList.add("d-none");
        forgotError.textContent = "";

        var idVal = forgotId.value.trim();
        var uType = forgotUserType.value;

        if (!idVal) {
          forgotError.textContent = "Please enter an ID.";
          return;
        }

        fetch("{% url 'security_questions' %}?id_number=" + encodeURIComponent(idVal))
          .then(function(r) { return r.json(); })
          .then(function(qData) {
            if (!qData.length) {
              forgotError.textContent = "User not found or no security questions.";
              return;
            }
            answeredQuestions = true;
            securityQuestions.classList.remove("d-none");

            var html = "";
            qData.forEach(function(obj) {
              html += `
                <label class="form-label fw-bold">${obj.question_text}</label>
                <input
                  type="text"
                  class="form-control mb-3 sqAnswer"
                  data-q="${obj.question_text}"
                >
              `;
            });
            securityQuestions.innerHTML = html;
          })
          .catch(function() {
            forgotError.textContent = "Error fetching questions.";
          });
      } else {
        var ansEls = document.querySelectorAll(".sqAnswer");
        var answers = [];
        ansEls.forEach(function(el) {
          answers.push({ question: el.dataset.q, answer: el.value.trim() });
        });

        var idVal = forgotId.value.trim();
        var uType = forgotUserType.value;

        if (!answers.length) {
          forgotError.textContent = "No answers entered.";
          return;
        }

        fetch("{% url 'forgot_password_check' %}", {
          method: "POST",
          headers: {
            "X-CSRFToken": "{{ csrf_token }}",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            id_number: idVal,
            user_type: uType,
            answers: answers
          })
        })
          .then(function(r) { return r.json(); })
          .then(function(d) {
            if (d.valid) {
              securityQuestions.classList.add("d-none");
              newPwFields.classList.remove("d-none");
              verifyBtn.textContent = "Update Password";

              verifyBtn.onclick = function() {
                var pw1 = document.getElementById("newPw").value.trim();
                var pw2 = document.getElementById("confirmPw").value.trim();

                if (!pw1 || !pw2) {
                  forgotError.textContent = "Enter both new password fields.";
                  return;
                }
                if (pw1 !== pw2) {
                  forgotError.textContent = "Passwords do not match.";
                  return;
                }

                fetch("{% url 'reset_password' %}", {
                  method: "POST",
                  headers: {
                    "X-CSRFToken": "{{ csrf_token }}",
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify({
                    id: idVal,
                    newPassword: pw1,
                    user_type: uType,
                    answers: answers
                  })
                })
                  .then(function(rr) { return rr.json(); })
                  .then(function(res) {
                    if (res.success) {
                      alert("Password updated successfully!");
                      window.location.reload();
                    } else {
                      forgotError.textContent = res.message || "Error resetting password.";
                    }
                  })
                  .catch(function() {
                    forgotError.textContent = "Server error. Please try again.";
                  });
              };
            } else {
              forgotError.textContent = "Answers did not match. Try again.";
            }
          })
          .catch(function() {
            forgotError.textContent = "Server error. Try again.";
          });
      }
    };
  }
});