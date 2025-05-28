
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
  }, 1000); // كل ثانية
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

function switchTab(tab) {
    document.querySelectorAll('.ai-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');

    document.getElementById('ai-notes').style.display = (tab === 'notes') ? 'block' : 'none';
    document.getElementById('ai-chat').style.display = (tab === 'chat') ? 'block' : 'none';
  }




// ⬇️ دالة الإرسال السريعة من الزر وتخفي الزر بعد الضغط
function sendQuick(questionText) {
  const button = event.target.closest("button"); // الزر الذي تم الضغط عليه
  if (button) button.style.display = "none";     // إخفاؤه

  sendQuestion(questionText); // أرسل السؤال
}

// ⬇️ الدالة العامة التي ترسل إما من input أو من زر
function sendQuestion(questionText = null) {
  const input = document.getElementById("user-question");
  const question = questionText || input.value.trim();  // استخدم من الزر أو من input
  const chatOutput = document.getElementById("chat-output");

  if (question === "") return;

  // 🧑‍💬 أضف رسالة المستخدم
  const userMsg = document.createElement("div");
  userMsg.className = "chat-message user";
  userMsg.innerHTML = `<span>🧑‍💬 ${question}</span>`;
  chatOutput.appendChild(userMsg);

  if (!questionText) input.value = "";  // امسح فقط إذا كان من input

  // ✅ جلب السكربت واللغة من hidden input
  const transcript = document.getElementById("transcript-data")?.value || "";
  const lang = document.getElementById("lang-data")?.value || "en";
  const direction = lang === "ar" ? "rtl" : "ltr";

  fetch("/chat-with-transcript", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question, transcript: transcript, lang: lang })
  })
    .then(res => res.json())
    .then(data => {
      const botMsg = document.createElement("div");
      botMsg.className = "chat-message bot";
      botMsg.innerHTML = `<span dir="${direction}">🤖 ${data.reply || data.error}</span>`;
      chatOutput.appendChild(botMsg);
      chatOutput.scrollTop = chatOutput.scrollHeight;
    });
}

// ⬇️ إرسال عند الضغط على Enter
document.getElementById("user-question").addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    e.preventDefault();
    sendQuestion();
  }
});

