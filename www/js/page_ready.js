// alternative to DOMContentLoaded event
// ref: https://developer.mozilla.org/en-US/docs/Web/API/Document/readyState
document.onreadystatechange = function () {
  if (document.readyState == "interactive") {
    update_mode();
    update_details();
  }
}