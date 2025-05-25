
document.querySelector(".summarize-form").addEventListener("submit", function (e) {
    const input = document.querySelector("input[name='url']").value;
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\//;

    if (!youtubeRegex.test(input.trim())) {
        e.preventDefault();
        alert("❌ Please enter a valid YouTube URL.");
    }
});

