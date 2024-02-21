$(document).ready(function () {
  console.log("Script executed!");
  $(".like-button").click(function () {
    let button = $(this);
    let recipeId = button.data("recipe-id");

    $.ajax({
      type: "POST",
      url: "/users/add_like/" + recipeId,
      success: function (data) {
        if (data.is_liked) {
          button.html(
            '<i class="fas fa-bookmark fa-x" style="color: red;"></i>'
          );
        } else {
          button.html('<i class="far fa-bookmark fa-x"></i>');
        }
      },
      error: function (error) {
        console.error("Error:", error);
      },
    });
  });
});

function toggleAdvancedSearch() {
  let basicSearchForm = document.getElementById("basicSearchForm");
  let advancedSearchForm = document.getElementById("advancedSearchForm");
  let advancedSearchButton = document.getElementById("advancedSearchButton");

  if (basicSearchForm.style.display === "none") {
    basicSearchForm.style.display = "block";
    advancedSearchForm.style.display = "none";
    if (advancedSearchButton) {
      advancedSearchButton.style.display = "block";
    }
  } else {
    basicSearchForm.style.display = "none";
    advancedSearchForm.style.display = "block";
    if (advancedSearchButton) {
      advancedSearchButton.style.display = "none";
    }
  }
}

function updateTimeOutputs() {
  // Get the range input value
  var selectedTime = document.getElementById("timeRange").value;

  // document.getElementById("minTimeOutput").textContent = "0 minutes";
  // document.getElementById("maxTimeOutput").textContent = "120 minutes";
  document.getElementById("selectedTimeOutput").textContent =
    selectedTime + " minutes";
}

// Initialize the time outputs on page load
updateTimeOutputs();
