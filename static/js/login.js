document.addEventListener("DOMContentLoaded", () => {
  const nextBtn = document.getElementById("signupNextBtn");
  const step1 = document.getElementById("signupStep1");
  const step2 = document.getElementById("signupStep2");
  const backBtn = document.getElementById("signupBackBtn");

  nextBtn?.addEventListener("click", () => {
    const inputs = step1.querySelectorAll("input:required");
    let valid = true;

    // Clear previous error messages
    step1.querySelectorAll(".invalid-feedback").forEach(el => el.remove());

    inputs.forEach((input) => {
      if (!input.value.trim()) {
        showError(input, "This field is required");
        valid = false;
      } else {
        input.classList.remove("is-invalid");
      }
    });

    // Custom checks
    const ageInput = step1.querySelector("input[name='age']");
    const ageValue = parseInt(ageInput?.value);
    if (ageValue < 18) {
      showError(ageInput, "You must be at least 18 years old");
      valid = false;
    }

    const pass1 = step1.querySelector("input[name='password1']");
    const pass2 = step1.querySelector("input[name='password2']");
    if (pass1 && pass2 && pass1.value !== pass2.value) {
      showError(pass2, "Passwords do not match");
      valid = false;
    }

    if (valid) {
      step1.classList.add("d-none");
      step2.classList.remove("d-none");
    }
  });

  backBtn?.addEventListener("click", () => {
    step2.classList.add("d-none");
    step1.classList.remove("d-none");
  });

  function showError(inputEl, message) {
    inputEl.classList.add("is-invalid");

    const feedback = document.createElement("div");
    feedback.className = "invalid-feedback";
    feedback.innerText = message;

    // Make sure feedback goes inside same parent (Bootstrap-compatible)
    inputEl.parentNode.appendChild(feedback);
  }

  // Login validation logic (already present)
  const loginForm = document.getElementById("loginForm");
  const showForgotBtn = document.getElementById("showForgotBtn");
  const loginError = document.getElementById("loginError");

  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const id_number = document.getElementById("id_number").value.trim();
      const password = document.getElementById("password").value;

      fetch("/ajax/validate-login/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ id_number, password })
      })
        .then(res => res.json())
        .then(data => {
          if (data.valid) {
            loginForm.submit();
          } else {
            loginError.textContent = data.message || "Invalid credentials.";
            if (data.user_exists && showForgotBtn) {
              showForgotBtn.classList.remove("d-none");
            }
          }
        })
        .catch(() => {
          loginError.textContent = "Something went wrong. Please try again.";
        });
    });
  }

  const applicantIcon = document.getElementById("applicantIcon");
const organizationIcon = document.getElementById("organizationIcon");
const applicantFields = document.querySelectorAll(".applicant-only");

  if (applicantIcon && organizationIcon) {
    applicantIcon.addEventListener("click", () => {
      applicantIcon.classList.add("active-type");
      organizationIcon.classList.remove("active-type");
      applicantFields.forEach(el => el.classList.remove("d-none"));
    });
  
    organizationIcon.addEventListener("click", () => {
      organizationIcon.classList.add("active-type");
      applicantIcon.classList.remove("active-type");
      applicantFields.forEach(el => el.classList.add("d-none"));
    });
  }
});
