
let player;

// تحميل سكربت YouTube API
let tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
document.body.appendChild(tag);

// لما يجهز مشغل الفيديو
window.onYouTubeIframeAPIReady = function () {
  player = new YT.Player("player", {
    events: {
      onReady: startTracking
    }
  });
};

// ✅ تتبع الوقت ومزامنة الكلمات
function startTracking() {
  setInterval(() => {
    if (player && typeof player.getCurrentTime === "function") {
      const currentTime = Math.floor(player.getCurrentTime());

      // ✅ تمييز الكلمة حسب الوقت
      document.querySelectorAll(".word").forEach(word => {
        const wordTime = parseInt(word.getAttribute("data-start"));
        if (wordTime === currentTime) {
          word.classList.add("highlighted");
          word.scrollIntoView({ behavior: "smooth", block: "center" });
        } else {
          word.classList.remove("highlighted");
        }
      });

      // ✅ تمييز السطر الكامل
      document.querySelectorAll(".line").forEach(line => {
        const lineStart = parseInt(line.getAttribute("data-start"));
        const nextLine = line.nextElementSibling;
        const nextStart = nextLine ? parseInt(nextLine.getAttribute("data-start")) : Infinity;

        if (currentTime >= lineStart && currentTime < nextStart) {
          line.classList.add("active");
        } else {
          line.classList.remove("active");
        }
      });
    }
  }, 2000); // كل ثانية
}

// ✅ عند النقر على الكلمة
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("word")) {
    const time = parseInt(e.target.getAttribute("data-start"));
    if (player && !isNaN(time)) {
      player.seekTo(time);
      player.playVideo();
    }
  }
});

// ✅ زر تحميل PDF
window.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("download-transcript");
  if (btn) {
    btn.addEventListener("click", function () {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      const summaryText = document.querySelector(".summary-html")?.innerText || "";
      const transcriptText = document.querySelector("#transcript-box")?.innerText || "";
      
      // فقط احذف الإيموجيات من الملخص
      const cleanSummary = summaryText.replaceAll("🧠", "").replaceAll("📜", "").replaceAll("💡", "");
      
      const fullText = `Summary:\n${cleanSummary}\n\nTranscript:\n${transcriptText}`;
      

      const lines = doc.splitTextToSize(fullText, 180);
      doc.text(lines, 15, 20);
      doc.save("video_summary_and_transcript.pdf");
    });
  }
});
