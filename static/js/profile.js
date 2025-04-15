document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("passwordModal");
    const stepChoice = document.getElementById("stepChoice");
    const stepVerifyOld = document.getElementById("stepVerifyOld");
    const stepSecurity = document.getElementById("stepSecurity");
    const stepNewPassword = document.getElementById("stepNewPassword");
    const btnRememberChoice = document.getElementById("btnRememberChoice");
    const btnForgotChoice = document.getElementById("btnForgotChoice");
    const btnSubmitVerifyOld = document.getElementById("btnSubmitVerifyOld");
    const btnSubmitSecurity = document.getElementById("btnSubmitSecurity");
    const btnBackToChoice1 = document.getElementById("btnBackToChoice1");
    const btnBackToChoice2 = document.getElementById("btnBackToChoice2");
    const btnBackToVerify = document.getElementById("btnBackToVerify");
    const verifyOldPwInput = document.getElementById("verifyOldPwInput");
    const inputNewPw1 = document.getElementById("inputNewPw1");
    const inputNewPw2 = document.getElementById("inputNewPw2");
    const verifyOldError = document.getElementById("verifyOldError");
    const securityError = document.getElementById("securityError");
    const pwMatchError = document.getElementById("pwMatchError");
    const openPasswordModal = document.getElementById("openPasswordModal");

    // Reset modal to initial state
    function resetModal() {
        stepChoice.style.display = "block";
        stepVerifyOld.style.display = "none";
        stepSecurity.style.display = "none";
        stepNewPassword.style.display = "none";
        verifyOldPwInput.value = "";
        inputNewPw1.value = "";
        inputNewPw2.value = "";
        document.querySelectorAll("#stepSecurity input[type='text']").forEach(input => input.value = "");
        verifyOldError.textContent = "";
        securityError.textContent = "";
        pwMatchError.textContent = "";
    }

    // Open modal
    openPasswordModal.addEventListener("click", function (e) {
        e.preventDefault();
        modal.style.display = "block";
        resetModal();
    });

    // Close modal on outside click
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            resetModal();
        }
    });

    // Choice: Remember old password
    btnRememberChoice.addEventListener("click", function () {
        stepChoice.style.display = "none";
        stepVerifyOld.style.display = "block";
        stepSecurity.style.display = "none";
        stepNewPassword.style.display = "none";
    });

    // Choice: Forgot old password
    btnForgotChoice.addEventListener("click", function () {
        stepChoice.style.display = "none";
        stepVerifyOld.style.display = "none";
        stepSecurity.style.display = "block";
        stepNewPassword.style.display = "none";
    });

    // Verify old password
    btnSubmitVerifyOld.addEventListener("click", function () {
        const password = verifyOldPwInput.value.trim();
        if (password) {
            fetch("/verify_password/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    stepChoice.style.display = "none";
                    stepVerifyOld.style.display = "none";
                    stepSecurity.style.display = "none";
                    stepNewPassword.style.display = "block";
                } else {
                    verifyOldError.textContent = "Incorrect password.";
                }
            })
            .catch(() => verifyOldError.textContent = "An error occurred.");
        } else {
            verifyOldError.textContent = "Please enter your current password.";
        }
    });

    // Verify security answers
    btnSubmitSecurity.addEventListener("click", function () {
        const answers = [];
        document.querySelectorAll("#stepSecurity input[type='text']").forEach(input => {
            const questionInput = input.nextElementSibling;
            const question = questionInput.value;
            const answer = input.value.trim();
            if (answer) answers.push({ question, answer });
        });
        if (answers.length >= 2) {
            fetch("/verify_security_answers/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ answers })
            })
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    stepChoice.style.display = "none";
                    stepVerifyOld.style.display = "none";
                    stepSecurity.style.display = "none";
                    stepNewPassword.style.display = "block";
                } else {
                    securityError.textContent = "At least two answers must be correct.";
                }
            })
            .catch(() => securityError.textContent = "An error occurred.");
        } else {
            securityError.textContent = "Please answer at least two security questions.";
        }
    });

    // Back buttons
    [btnBackToChoice1, btnBackToChoice2, btnBackToVerify].forEach(btn => {
        btn.addEventListener("click", resetModal);
    });

    // Live password match validation
    function checkPasswordMatch() {
        const pw1 = inputNewPw1.value;
        const pw2 = inputNewPw2.value;
        pwMatchError.textContent = (pw1 && pw2 && pw1 !== pw2) ? "Passwords do not match." : "";
    }
    inputNewPw1.addEventListener("input", checkPasswordMatch);
    inputNewPw2.addEventListener("input", checkPasswordMatch);

    // CSRF token utility
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});