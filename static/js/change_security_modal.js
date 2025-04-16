document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("changeSecurityModal");
  if (!modal) return;

  const step1 = document.getElementById("securityStep1");
  const step2 = document.getElementById("securityStep2");
  const progressBar = document.getElementById("securityProgress");

  const confirmPwInput = document.getElementById("secConfirmPwInput");
  const confirmPwError = document.getElementById("secConfirmPwError");
  const secUpdateError = document.getElementById("secUpdateError");

  const newQuestionsContainer = document.getElementById("newQuestionsContainer");
  const verifyCurrentPwBtn = document.getElementById("verifySecCurrentPw");
  const backBtn = document.getElementById("backToSecStep1");
  const updateForm = document.getElementById("securityUpdateForm");

  const userId = document.getElementById("userIdNumber")?.value;
  const userType = document.getElementById("userType")?.value;

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function showStep1() {
    step1.classList.remove("d-none");
    step2.classList.add("d-none");
    progressBar.style.width = "50%";
  }

  function showStep2() {
    step1.classList.add("d-none");
    step2.classList.remove("d-none");
    progressBar.style.width = "100%";
  }

  verifyCurrentPwBtn.addEventListener("click", () => {
    const password = confirmPwInput.value.trim();
    confirmPwError.textContent = "";

    if (!password) {
      confirmPwError.textContent = "Please enter your password.";
      return;
    }

    fetch("/verify_password/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.valid) {
          showStep2();
          loadQuestions();
        } else {
          confirmPwError.textContent = "Incorrect password.";
        }
      })
      .catch(() => {
        confirmPwError.textContent = "Server error. Try again.";
      });
  });

  function loadQuestions() {
    newQuestionsContainer.innerHTML = "";
  
    fetch("/get_security_questions_choices/")
      .then((res) => res.json())
      .then((categories) => {
        for (let i = 0; i < 3; i++) {
          const qDiv = document.createElement("div");
          qDiv.className = "mb-3";
  
          const options = categories[i]
            .map(
              (q) => `<option value="${q.id}|${q.text}">${q.text}</option>`
            )
            .join("");
  
          qDiv.innerHTML = `
            <label class="form-label">Question ${i + 1}</label>
            <select name="question_${i + 1}" class="form-select mb-2">
              <option value="">-- Select a question --</option>
              ${options}
            </select>
            <input type="text" name="answer_${i + 1}" class="form-control" placeholder="Your answer" required>
          `;
          newQuestionsContainer.appendChild(qDiv);
        }
      })
      .catch(() => {
        secUpdateError.textContent = "Failed to load questions.";
      });
  }
  
  
  backBtn.addEventListener("click", () => {
    showStep1();
    secUpdateError.textContent = "";
    newQuestionsContainer.innerHTML = "";
  });

  updateForm.addEventListener("submit", function (e) {
    e.preventDefault();
    secUpdateError.textContent = "";

    const formData = new FormData(updateForm);
    const questions = [];

    for (let i = 1; i <= 3; i++) {
      const q = formData.get(`question_${i}`);
      const a = formData.get(`answer_${i}`).trim();
      if (q && a) {
        questions.push({ question_id: q, answer: a });
      }
    }

    if (questions.length < 2) {
      secUpdateError.textContent = "Please fill at least 2 questions and answers.";
      return;
    }

    fetch("/update_security_questions/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        id_number: userId,
        user_type: userType,
        questions
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          alert("Security questions updated!");
          bootstrap.Modal.getInstance(modal).hide();
        } else {
          secUpdateError.textContent = data.message || "Update failed.";
        }
      })
      .catch(() => {
        secUpdateError.textContent = "Something went wrong.";
      });
  });

  const openSecurityBtn = document.getElementById("openSecurityModal");
  if (openSecurityBtn) {
    openSecurityBtn.addEventListener("click", () => {
      const modalEl = document.getElementById("changeSecurityModal");
      const modal = new bootstrap.Modal(modalEl);
      modal.show();

      document.getElementById("securityStep1").classList.remove("d-none");
      document.getElementById("securityStep2").classList.add("d-none");
      document.getElementById("securityProgress").style.width = "50%";

      document.getElementById("secConfirmPwInput").value = "";
      document.getElementById("secConfirmPwError").textContent = "";
      document.getElementById("secUpdateError").textContent = "";
      document.getElementById("newQuestionsContainer").innerHTML = "";
    });
  }
});
