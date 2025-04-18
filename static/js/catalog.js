document.addEventListener("DOMContentLoaded", function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function showCustomAlert(message) {
    const alertBox = document.getElementById("customAlert");
    alertBox.textContent = message;
    alertBox.classList.add("show");
    setTimeout(() => {
      alertBox.classList.remove("show");
    }, 2500);
  }

  document.querySelectorAll(".apply-btn[data-job-id]").forEach((btn) => {
    if (btn.dataset.bound === "true") return;
    btn.dataset.bound = "true";

    btn.addEventListener("click", function (e) {
      e.stopPropagation(); // ✅ stop bubbling up
      e.preventDefault();

      const jobId = btn.getAttribute("data-job-id");
      const jobCard = btn.closest(".job-card");

      if (!jobId || jobId === "null") {
        alert("Job ID missing. Please refresh the page.");
        return;
      }

      // Immediately disable
      btn.disabled = true;
      btn.textContent = "Applying...";

      fetch(`/account/apply/${jobId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({}),
      })
        .then((res) => res.json().then(data => ({ status: res.status, body: data })))
        .then(({ status, body }) => {
          if (status === 200 && body.success) {
            btn.textContent = "Applied!";
            btn.classList.add("disabled");
            if (jobCard) jobCard.remove();
            showCustomAlert("Successfully Applied!");
          } else {
            const isCustomVisible = document.getElementById("customAlert").classList.contains("show");
            if (!isCustomVisible) {
              alert(body.message || "You already applied.");
            }
            btn.disabled = false;
            btn.textContent = "Apply";
          }
        })
        .catch(() => {
          alert("Error applying. Please try again.");
          btn.disabled = false;
          btn.textContent = "Apply";
        });
    });
  });

  // Optional: chat button handling
  document.querySelectorAll(".chat-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      window.location.href = "/chat/";
    });
  });
});
