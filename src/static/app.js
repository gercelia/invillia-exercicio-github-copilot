document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = "";

      Object.entries(activities).forEach(([name, details]) => {
        const spotsLeft = details.max_participants - details.participants.length;

        // Exibir todas as atividades no dropdown, mesmo sem participantes
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);

        // Remova o card se não houver participantes
        if (details.participants.length === 0) {
          return;
        }

        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <p><strong>Participants:</strong></p>
          <ul class="participants-list">
            ${
              details.participants.map(participant => `
                <li>
                  ${participant}
                  <button class="cancel-button" data-activity="${name}" data-email="${participant}">
                    Cancel
                  </button>
                  <button class="edit-email-button" data-activity="${name}" data-email="${participant}">
                    Edit Email
                  </button>
                </li>
              `).join("")
            }
          </ul>
        `;

        activitiesList.appendChild(activityCard);
      });

      document.querySelectorAll(".cancel-button").forEach(button => {
        button.addEventListener("click", (event) => {
          const activity = event.target.dataset.activity;
          const email = event.target.dataset.email;
          cancelSignup(activity, email);
        });
      });

      document.querySelectorAll(".edit-email-button").forEach(button => {
        button.addEventListener("click", (event) => {
          const activity = event.target.dataset.activity;
          const oldEmail = event.target.dataset.email;
          const newEmail = prompt("Enter the new email:", oldEmail);

          if (newEmail && newEmail !== oldEmail) {
            editEmail(activity, oldEmail, newEmail);
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function cancelSignup(activity, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/cancel?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to cancel signup. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error canceling signup:", error);
    }
  }

  async function editEmail(activity, oldEmail, newEmail) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/edit-email`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ old_email: oldEmail, new_email: newEmail }),
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        // Após a edição do email, a função fetchActivities é chamada para atualizar a lista de participantes.
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to edit email. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error editing email:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});
