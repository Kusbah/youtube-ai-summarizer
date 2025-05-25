document.querySelector(".summarize-btn").addEventListener("click", function () {
    const input = document.querySelector(".input-wrapper input");
    const url = input.value.trim();
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\//;

    // إزالة أي رسالة خطأ سابقة
    removeErrorMessage();

    if (!youtubeRegex.test(url)) {
        // عرض رسالة خطأ
        showErrorMessage("Please enter a valid YouTube URL.");
    } else {
        console.log("✅ Valid YouTube URL:", url);
        // ✅ انتقال إلى صفحة summary
        window.location.href = "summary.html";
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
