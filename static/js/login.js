document.addEventListener("DOMContentLoaded", () => {
  const applicantIcon = document.getElementById("applicantIcon");
  const organizationIcon = document.getElementById("organizationIcon");
  const applicantFields = document.querySelectorAll(".applicant-only");
  const orgFields = document.querySelectorAll(".org-only");
  const userTypeInput = document.getElementById("user_type");

  const step1 = document.getElementById("signupStep1");
  const step2 = document.getElementById("signupStep2");
  const nextBtn = document.getElementById("signupNextBtn");
  const signupForm = document.getElementById("signupForm");

  const backBtn = document.getElementById("signupBackBtn");

  
  backBtn?.addEventListener("click", () => {
  // Show Step 1 again
  step2.classList.add("d-none");
  step1.classList.remove("d-none");

  // Re-enable user type switch
  applicantIcon.classList.remove("disabled", "pe-none", "opacity-50");
  organizationIcon.classList.remove("disabled", "pe-none", "opacity-50");

  // Hide Back button
  backBtn.classList.add("d-none");
});

  // Set default to applicant
  userTypeInput.value = "job_seeker";
  applicantFields.forEach(f => f.classList.remove("d-none"));
  orgFields.forEach(f => f.classList.add("d-none"));

  applicantIcon?.addEventListener("click", () => {
    userTypeInput.value = "job_seeker";
    applicantIcon.classList.add("active-type");
    organizationIcon.classList.remove("active-type");
    applicantFields.forEach(f => f.classList.remove("d-none"));
    orgFields.forEach(f => f.classList.add("d-none"));
  });

  organizationIcon?.addEventListener("click", () => {
    userTypeInput.value = "job_poster";
    organizationIcon.classList.add("active-type");
    applicantIcon.classList.remove("active-type");
    orgFields.forEach(f => f.classList.remove("d-none"));
    applicantFields.forEach(f => f.classList.add("d-none"));
  });

  nextBtn?.addEventListener("click", () => {
    const pw1 = step1.querySelector("input[name='password1']");
    const pw2 = step1.querySelector("input[name='password2']");
  
    if (pw1.value !== pw2.value) {
      alert("Passwords do not match.");
      return;
    }
  
    if (pw1.value.length < 8) {
      alert("Password must be at least 8 characters.");
      return;
    }
  
    // Hide step 1, show step 2
    step1.classList.add("d-none");
    step2.classList.remove("d-none");
  
    // Lock the user type selection
    applicantIcon.classList.add("disabled", "pe-none", "opacity-50");
    organizationIcon.classList.add("disabled", "pe-none", "opacity-50");
  
    // Show relevant fields
    if (userTypeInput.value === "job_seeker") {
      applicantFields.forEach(f => f.classList.remove("d-none"));
      orgFields.forEach(f => f.classList.add("d-none"));
    } else {
      orgFields.forEach(f => f.classList.remove("d-none"));
      applicantFields.forEach(f => f.classList.add("d-none"));
    }
  
    // Show Back button
    document.getElementById("signupBackBtn").classList.remove("d-none");
  });
  

  // Load security question dropdowns
  const loadSecurityQuestions = () => {
    fetch("/account/security-questions/")
      .then(res => res.json())
      .then(data => {
        const q1 = document.querySelector("select[name='question1_subquestion']");
        const q2 = document.querySelector("select[name='question2_subquestion']");
        const q3 = document.querySelector("select[name='question3_subquestion']");
  
        q1.innerHTML = "";
        q2.innerHTML = "";
        q3.innerHTML = "";
  
        // Expected order: index 0 => Question 1, 1 => Question 2, 2 => Question 3
        if (data.length >= 3) {
          const [qData1, qData2, qData3] = data;
  
          [qData1.option1, qData1.option2, qData1.option3].forEach(opt => {
            const el = document.createElement("option");
            el.value = opt;
            el.textContent = opt;
            q1.appendChild(el);
          });
  
          [qData2.option1, qData2.option2, qData2.option3].forEach(opt => {
            const el = document.createElement("option");
            el.value = opt;
            el.textContent = opt;
            q2.appendChild(el);
          });
  
          [qData3.option1, qData3.option2, qData3.option3].forEach(opt => {
            const el = document.createElement("option");
            el.value = opt;
            el.textContent = opt;
            q3.appendChild(el);
          });
        }
      });
  };
  

  loadSecurityQuestions();

  // Submit signup form
  signupForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(signupForm);

    fetch("/account/register/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
      },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Registration successful!");
        location.href = "/dashboard/";
      } else {
        alert("Registration failed: " + JSON.stringify(data.errors || data.message));
      }
    })
    .catch(() => {
      alert("Something went wrong. Please try again.");
    });
  });

  // Forgot password logic
  const verifyBtn = document.getElementById("verifyBtn");
  const forgotIdInput = document.getElementById("forgotId");
  const forgotError = document.getElementById("forgotError");
  const securityBox = document.getElementById("securityQuestions");
  const newPwBox = document.getElementById("newPwFields");

  verifyBtn?.addEventListener("click", () => {
    const passportId = forgotIdInput.value.trim();
    fetch(`/account/forgot-password/?id=${passportId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          securityBox.innerHTML = "";
          data.questions.forEach(q => {
            const input = document.createElement("input");
            input.className = "form-control my-2";
            input.placeholder = q;
            input.setAttribute("data-question", q);
            input.required = true;
            securityBox.appendChild(input);
          });

          securityBox.classList.remove("d-none");
          newPwBox.classList.remove("d-none");

          verifyBtn.textContent = "Reset Password";
          verifyBtn.onclick = () => {
            const answers = Array.from(securityBox.querySelectorAll("input")).map(input => ({
              question: input.dataset.question,
              answer: input.value
            }));

            const newPassword = document.getElementById("newPw").value;
            const confirmPassword = document.getElementById("confirmPw").value;

            if (newPassword !== confirmPassword || newPassword.length < 8) {
              forgotError.textContent = "Passwords don't match or are too short.";
              return;
            }

            fetch("/account/reset-password/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
              },
              body: JSON.stringify({ id: passportId, answers, newPassword })
            })
            .then(res => res.json())
            .then(r => {
              if (r.success) {
                alert("Password updated! Please login.");
                location.reload();
              } else {
                forgotError.textContent = r.message || "Security answers incorrect.";
              }
            });
          };
        } else {
          forgotError.textContent = "Passport ID not found.";
        }
      })
      .catch(() => {
        forgotError.textContent = "Something went wrong.";
      });
  });
});

