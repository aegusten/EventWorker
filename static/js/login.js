document.addEventListener("DOMContentLoaded", function() {
  var applicantIcon = document.getElementById("applicantIcon");
  var organizationIcon = document.getElementById("organizationIcon");
  var userTypeInput = document.getElementById("user_type");
  var applicantOnly = document.querySelectorAll(".applicant-only");
  var orgOnly = document.querySelectorAll(".org-only");
  var step1 = document.getElementById("signupStep1");
  var step2 = document.getElementById("signupStep2");
  var signupNextBtn = document.getElementById("signupNextBtn");
  var signupBackBtn = document.getElementById("signupBackBtn");

  // Switch to applicant view
  if (applicantIcon) {
    applicantIcon.onclick = function() {
      userTypeInput.value = "applicant";
      applicantIcon.classList.add("active-type");
      organizationIcon.classList.remove("active-type");
      applicantOnly.forEach(function(el) { el.classList.remove("d-none"); });
      orgOnly.forEach(function(el) { el.classList.add("d-none"); });
    };
  }

  // Switch to organization view
  if (organizationIcon) {
    organizationIcon.onclick = function() {
      userTypeInput.value = "organization";
      organizationIcon.classList.add("active-type");
      applicantIcon.classList.remove("active-type");
      orgOnly.forEach(function(el) { el.classList.remove("d-none"); });
      applicantOnly.forEach(function(el) { el.classList.add("d-none"); });
    };
  }

  // Move to Step 2 (and show relevant fields)
  if (signupNextBtn) {
    signupNextBtn.onclick = function() {
      step1.classList.add("d-none");
      step2.classList.remove("d-none");

      if (userTypeInput.value === "applicant") {
        applicantOnly.forEach(function(el) { el.classList.remove("d-none"); });
      } else {
        orgOnly.forEach(function(el) { el.classList.remove("d-none"); });
      }
    };
  }

  // Move back to Step 1
  if (signupBackBtn) {
    signupBackBtn.onclick = function() {
      step2.classList.add("d-none");
      step1.classList.remove("d-none");

      if (userTypeInput.value === "applicant") {
        orgOnly.forEach(function(el) { el.classList.add("d-none"); });
      } else {
        applicantOnly.forEach(function(el) { el.classList.add("d-none"); });
      }
    };
  }

  // Forgot password logic
  var forgotId = document.getElementById("forgotId");
  var forgotUserType = document.getElementById("forgotUserType");
  var securityQuestions = document.getElementById("securityQuestions");
  var newPwFields = document.getElementById("newPwFields");
  var forgotError = document.getElementById("forgotError");
  var verifyBtn = document.getElementById("verifyBtn");
  var answeredQuestions = false;

  if (verifyBtn) {
    verifyBtn.onclick = function() {
      // First click => fetch + display questions
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
      }
      // Second click => verify answers
      else {
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
              // Show password update fields
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
