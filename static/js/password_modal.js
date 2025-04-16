document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("changePasswordModal");
    if (!modalEl) return;
  
    const modal = new bootstrap.Modal(modalEl);
  
    const step1 = document.getElementById("pwStep1");
    const step2Old = document.getElementById("pwStep2Old");
    const step2Sec = document.getElementById("pwStep2Sec");
    const step3 = document.getElementById("pwStep3");
  
    const progress = document.getElementById("changePwProgress");
  
    const btnUseOldPw = document.getElementById("btnUseOldPw");
    const btnUseSecQ = document.getElementById("btnUseSecQ");
    const backStep1a = document.getElementById("backStep1a");
    const backStep1b = document.getElementById("backStep1b");
    const verifyCurrentPw = document.getElementById("verifyCurrentPw");
    const verifySecAnswers = document.getElementById("verifySecAnswers");
    const backStep2 = document.getElementById("backStep2");
  
    const currentPwInput = document.getElementById("currentPwInput");
    const currentPwError = document.getElementById("currentPwError");
  
    const secQuestionsBox = document.getElementById("secQuestionsBox");
    const secAnswersError = document.getElementById("secAnswersError");
  
    const newPw1 = document.getElementById("newPw1");
    const newPw2 = document.getElementById("newPw2");
    const finalPwError = document.getElementById("finalPwError");
  
    const finalPwForm = document.getElementById("finalPwForm");
    const userId = document.getElementById("userIdNumber")?.value;
    const userType = document.getElementById("userType")?.value;
    let method = null;

    function validatePasswordMatch() {
      if (newPw1.value && newPw2.value && newPw1.value !== newPw2.value) {
        finalPwError.textContent = "Passwords do not match.";
      } else {
        finalPwError.textContent = "";
      }
    }
    
    newPw1.addEventListener("input", validatePasswordMatch);
    newPw2.addEventListener("input", validatePasswordMatch);
    
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
  
    function showStep(stepToShow) {
      [step1, step2Old, step2Sec, step3].forEach(step => step.classList.add("d-none"));
      stepToShow.classList.remove("d-none");
    }
  
    function updateProgress(percent) {
      progress.style.width = percent;
    }
  
    btnUseOldPw.onclick = () => {
      method = "old";
      showStep(step2Old);
      updateProgress("66%");
    };
  
    btnUseSecQ.onclick = () => {
      method = "security";
      showStep(step2Sec);
      updateProgress("66%");

    fetch(`/get_security_questions/?id_number=${userId}`)
      .then(res => res.json())
      .then(data => {
        secQuestionsBox.innerHTML = "";
        data.forEach(q => {
          const el = document.createElement("div");
          el.className = "mb-3";
          el.innerHTML = `
            <label class="form-label">${q.question_text}</label>
            <input type="text" class="form-control sec-answer" data-id="${q.id}" placeholder="Your answer">
          `;
          secQuestionsBox.appendChild(el);
        });        
      });
    };
  
    backStep1a.onclick = () => {
      currentPwInput.value = "";
      currentPwError.textContent = "";
      showStep(step1);
      updateProgress("33%");
    };
  
    backStep1b.onclick = () => {
      secAnswersError.textContent = "";
      secQuestionsBox.innerHTML = "";
      showStep(step1);
      updateProgress("33%");
    };
  
    verifyCurrentPw.onclick = () => {
      currentPwError.textContent = "";
      const password = currentPwInput.value.trim();
      if (!password) {
        currentPwError.textContent = "Please enter your current password.";
        return;
      }
  
      fetch("/verify_password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ password })
      })
        .then(res => res.json())
        .then(data => {
          if (data.valid) {
            showStep(step3);
            updateProgress("100%");
          } else {
            currentPwError.textContent = "Incorrect password.";
          }
        })
        .catch(() => {
          currentPwError.textContent = "Server error.";
        });
    };
  
    verifySecAnswers.onclick = () => {
      secAnswersError.textContent = "";
  
      const answers = [];
      document.querySelectorAll(".sec-answer").forEach(input => {
        const questionId = input.getAttribute("data-id");
        const answer = input.value.trim();
        if (questionId && answer) {
          answers.push({ question_id: questionId, answer });
        }
      });      
  
      if (answers.length < 2) {
        secAnswersError.textContent = "Answer at least 2 questions.";
        return;
      }
  
      fetch("/verify_security_answers/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
          id_number: userId,
          user_type: userType,
          answers
        })
      })
        .then(res => res.json())
        .then(data => {
          if (data.valid) {
            showStep(step3);
            updateProgress("100%");
          } else {
            secAnswersError.textContent = "Answers incorrect.";
          }
        })
        .catch(() => {
          secAnswersError.textContent = "Server error.";
        });
    };
  
    backStep2.onclick = () => {
      if (method === "old") {
        showStep(step2Old);
        updateProgress("66%");
      } else {
        showStep(step2Sec);
        updateProgress("66%");
      }
    };
  
    finalPwForm.addEventListener("submit", function (e) {
      e.preventDefault();
      finalPwError.textContent = "";
  
      const pw1 = newPw1.value.trim();
      const pw2 = newPw2.value.trim();
  
      if (!pw1 || !pw2) {
        finalPwError.textContent = "Please fill in both fields.";
        return;
      }
  
      if (pw1 !== pw2) {
        finalPwError.textContent = "Passwords do not match.";
        return;
      }
  
      const formData = new FormData();
      formData.append("new_password1", pw1);
      formData.append("new_password2", pw2);
  
      fetch("{% url 'change_password' %}", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: formData
      })
        .then(res => {
          if (res.redirected) {
            window.location.href = res.url;
          } else {
            alert("Password changed successfully!");
            modal.hide();
          }
        })
        .catch(() => {
          finalPwError.textContent = "Something went wrong.";
        });
    });
  
    const openBtn = document.getElementById("openPasswordModal");
    if (openBtn) {
      openBtn.addEventListener("click", () => {
        showStep(step1);
        updateProgress("33%");
        modal.show();
      });
    }
  });
  