document.addEventListener("DOMContentLoaded", function () {
  const chatButtons = document.querySelectorAll(".chat-btn");

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

  document.addEventListener("click", function (e) {
    const applyBtn = e.target.closest(".apply-btn[data-job-id]");
    if (!applyBtn) return;

    e.preventDefault();
    const jobId = applyBtn.getAttribute("data-job-id");
    const jobCard = applyBtn.closest(".job-card");

    if (!jobId || jobId === "null") {
      alert("Job ID missing. Please refresh the page.");
      return;
    }

    fetch(`/account/apply/${jobId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({}),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          if (jobCard) jobCard.remove(); 
          showCustomAlert("Successfully Applied!");
        } else {
          alert(data.message || "You already applied.");
        }
      })
      .catch(() => {
        alert("Error applying to job. Try again.");
      });
  });

  chatButtons.forEach((button) => {
    button.addEventListener("click", function () {
      window.location.href = "/chat/";
    });
  });
});
