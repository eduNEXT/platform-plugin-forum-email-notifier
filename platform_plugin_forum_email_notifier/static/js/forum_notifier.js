function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

$(".email-notifications-select").on("change", function (select) {
  fetch("instructor/api/forum_email_notification_preference", {
    method: "PUT",
    body: JSON.stringify({
      preference: parseInt($(this).val()),
    }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      console.log(data);
    });
});

$(function () {
  const cssUrl = "https://cdn.jsdelivr.net/npm/@edx/paragon@20.45.5/dist/paragon.min.css";

  $("<link>")
    .attr({
      href: cssUrl,
      rel: "stylesheet",
    })
    .appendTo("head");
});
