$(document).ready(function () {
  console.log("Script executed!");
  $(".like-button").click(function () {
    let button = $(this);
    let recipeId = button.data("recipe-id");

    if ($("#user-status").length > 0) {
      $.ajax({
        type: "POST",
        url: "/users/add_like/" + recipeId,
        success: function (data) {
          if (data.is_liked) {
            button.html(
              '<i class="fa-solid fa-bookmark fa-xl" style="color: #ff0000;"></i>'
            );
          } else {
            button.html('<i class="fa-regular fa-bookmark fa-xl"></i>');
          }
        },
        error: function (error) {
          console.error("Error:", error);
        },
      });
    } else {
      alert("Log in first");
    }
  });
});

function toggleAdvancedSearch() {
  let basicSearchForm = document.getElementById("basicSearchForm");
  let advancedSearchForm = document.getElementById("advancedSearchForm");
  let advancedSearchButton = document.getElementById("advancedSearchButton");
  let hideAdvancedSearchButton = document.getElementById(
    "hideAdvancedSearchButton"
  );

  if (basicSearchForm.style.display === "none") {
    basicSearchForm.style.display = "block";
    advancedSearchForm.style.display = "none";
    advancedSearchButton.style.display = "block";
    hideAdvancedSearchButton.style.display = "none";
  } else {
    basicSearchForm.style.display = "none";
    advancedSearchForm.style.display = "block";
    advancedSearchButton.style.display = "none";
    hideAdvancedSearchButton.style.display = "inline-block";
  }
}

function hideAdvancedSearch() {
  let basicSearchForm = document.getElementById("basicSearchForm");
  let advancedSearchForm = document.getElementById("advancedSearchForm");
  let advancedSearchButton = document.getElementById("advancedSearchButton");
  let hideAdvancedSearchButton = document.getElementById(
    "hideAdvancedSearchButton"
  );

  basicSearchForm.style.display = "block";
  advancedSearchForm.style.display = "none";
  advancedSearchButton.style.display = "block";
  hideAdvancedSearchButton.style.display = "none";
}

function updateTimeOutputs() {
  var selectedTime = document.getElementById("timeRange").value;
  document.getElementById("selectedTimeOutput").textContent =
    selectedTime + " minutes";
}

updateTimeOutputs();

document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".ingredient-checkbox");

  checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      const label = this.nextElementSibling;
      label.style.textDecoration = this.checked ? "line-through" : "none";
      label.style.color = this.checked ? black : "";
    });
  });
});
