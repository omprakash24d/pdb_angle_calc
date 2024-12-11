$(document).ready(function () {
  const $contactForm = $("#contactForm");
  const $submitBtn = $("#submitBtn");
  const $loadingSpinner = $("#loadingSpinner");
  const $successMessage = $("#successMessage");

  $contactForm.on("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Disable the submit button and show the loading spinner
    $submitBtn.prop("disabled", true);
    $loadingSpinner.show();

    // Serialize the form data
    const formData = $contactForm.serialize();

    // Send the form data via AJAX
    $.ajax({
      url: "https://docs.google.com/forms/d/e/1FAIpQLSeDOM4IASvYC33epLAs5tbtd4LLmGWrEIaKfCaSDGN0NHVQwg/formResponse",
      type: "POST",
      data: formData,
      dataType: "xml",
      success: handleSuccess,
      error: handleError
    });
  });

  function handleSuccess() {
    showSuccessMessage();
  }

  function handleError() {
    showSuccessMessage();
  }

  function showSuccessMessage() {
    $successMessage.show();
    $contactForm[0].reset(); // Reset the form fields
    $submitBtn.prop("disabled", false); // Re-enable the button
    $loadingSpinner.hide(); // Hide the loading spinner
  }
});
