document.addEventListener("DOMContentLoaded", function () {
  const startBtn = document.getElementById("startSecQFlow");
  const idInput = document.getElementById("forgotId");
  const errorBox = document.getElementById("forgotError");
  const step1 = document.getElementById("pwStep1IdOnly");
  const step2 = document.getElementById("pwStep2Sec");
  const step3 = document.getElementById("pwStep3");
  const questionsBox = document.getElementById("secQuestionsBox");

  const verifySecAnswersBtn = document.getElementById("verifySecAnswers");
  const backToIdInputBtn = document.getElementById("backToIdInput");
  const backStep2Btn = document.getElementById("backStep2");

  let userId = "";
  let userType = "";
  let currentQuestions = [];

  // Step 1 → Step 2
  startBtn.addEventListener("click", () => {
    errorBox.textContent = "";
    userId = idInput.value.trim();

    if (!userId) {
      errorBox.textContent = "Please enter your ID.";
      return;
    }

    // Determine user type from backend
    fetch(`/get_security_questions/?id_number=${encodeURIComponent(userId)}`)
      .then(res => res.json())
      .then(data => {
        if (!data.length) {
          errorBox.textContent = "User not found or no security questions set.";
          return;
        }

        step1.classList.add("d-none");
        step2.classList.remove("d-none");

        currentQuestions = data;
        userType = data.length ? 'applicant' : 'organization'; // your backend can send user type if needed

        questionsBox.innerHTML = "";
        data.forEach(q => {
          questionsBox.innerHTML += `
            <label class="form-label">${q.question_text}</label>
            <input type="text" class="form-control mb-2 sqAnswer" data-qid="${q.id}">
          `;
        });
      });
  });

  // Step 2 → Step 3
  verifySecAnswersBtn.addEventListener("click", () => {
    const answers = [];
    document.querySelectorAll(".sqAnswer").forEach(input => {
      answers.push({ question_id: input.dataset.qid, answer: input.value.trim() });
    });

    fetch(`/verify_security_answers/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ id_number: userId, answers, user_type: userType })
    })
    .then(res => res.json())
    .then(result => {
      if (result.valid) {
        step2.classList.add("d-none");
        step3.classList.remove("d-none");
      } else {
        document.getElementById("secAnswersError").textContent = "Your answers did not match. Try again.";
      }
    });
  });

  // Final password submit
  document.getElementById("finalPwForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const pw1 = document.getElementById("newPw1").value;
    const pw2 = document.getElementById("newPw2").value;
    const errorDiv = document.getElementById("finalPwError");

    if (!pw1 || !pw2) {
      errorDiv.textContent = "Please fill in both password fields.";
      return;
    }
    if (pw1 !== pw2) {
      errorDiv.textContent = "Passwords do not match.";
      return;
    }

    fetch(`/reset_password/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ id: userId, newPassword: pw1, user_type: userType, answers: [] })
    })
      .then(res => res.json())
      .then(result => {
        if (result.success) {
          alert("✅ Password updated!");
          location.reload();
        } else {
          errorDiv.textContent = result.message || "Failed to reset password.";
        }
      });
  });

  // Back buttons
  backToIdInputBtn.onclick = () => {
    step2.classList.add("d-none");
    step1.classList.remove("d-none");
  };

  backStep2Btn.onclick = () => {
    step3.classList.add("d-none");
    step2.classList.remove("d-none");
  };
});
