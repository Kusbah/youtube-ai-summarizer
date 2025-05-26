document.querySelector("form").addEventListener("submit", function (e) {
    const urlInput = document.getElementById("youtube-url");
    const url = urlInput.value.trim();
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;

    if (!youtubeRegex.test(url)) {
        e.preventDefault();  // ❌ امنع الإرسال
        document.querySelector(".error-message").textContent = "Please enter a valid YouTube URL.";
    }
});

function showErrorMessage(message) {
    const existing = document.querySelector(".error-message");
    if (existing) existing.remove();

    const error = document.createElement("div");
    error.classList.add("error-message");
    error.textContent = message;

    const content = document.querySelector(".content");
    content.insertBefore(error, content.firstChild);
}

function removeErrorMessage() {
    const existing = document.querySelector(".error-message");
    if (existing) existing.remove();
}
