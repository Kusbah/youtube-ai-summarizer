document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("compare-input");
    const output = document.getElementById("chat-output");
    const transcript1 = document.getElementById("transcript1-data").value;
    const transcript2 = document.getElementById("transcript2-data").value;
  
    // إرسال بالإنتر
    input.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        sendCompareQuestion();
      }
    });
  
    // إرسال مقارنة تلقائية عند فتح الصفحة
    if (!transcript1 || !transcript2) {
      addBotMessage("⚠️ One or both transcripts are missing.");
      return;
    }
  
    addUserMessage("📊 Compare these two videos");
  
    fetch("/compare-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: "compare",
        transcript1: transcript1,
        transcript2: transcript2,
        is_first: true
      }),
    })
      .then(res => res.json())
      .then(data => {
        addBotMessage(data.reply || "⚠️ Could not get AI comparison.");
      })
      .catch(err => {
        addBotMessage("❌ Error occurred.");
        console.error(err);
      });
  });
  
  function addUserMessage(msg) {
    const output = document.getElementById("chat-output");
    const div = document.createElement("div");
    div.className = "chat-message user";
    div.innerText = msg;
    output.appendChild(div);
  }
  
  function addBotMessage(msg) {
    const output = document.getElementById("chat-output");
    const div = document.createElement("div");
    div.className = "chat-message bot";
    div.innerHTML = msg; // ضروري نخليها innerHTML عشان الجداول
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
  }
  
  async function sendCompareQuestion() {
    const input = document.getElementById("compare-input");
    const output = document.getElementById("chat-output");
    const question = input.value.trim();
    const transcript1 = document.getElementById("transcript1-data").value;
    const transcript2 = document.getElementById("transcript2-data").value;
  
    if (!question || !transcript1 || !transcript2) {
      addBotMessage("❌ Transcripts missing. Cannot compare properly.");
      return;
    }
  
    addUserMessage(question);
    input.value = "";
  
    try {
      const res = await fetch("/compare-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          transcript1: transcript1,
          transcript2: transcript2
        }),
      });
  
      const data = await res.json();
      addBotMessage(data.reply || "❌ Failed to get comparison.");
    } catch (error) {
      addBotMessage("❌ Error occurred.");
    }
  }
  
  function compareVideos() {
    const transcript1 = document.getElementById("transcript1-data").value;
    const transcript2 = document.getElementById("transcript2-data").value;
    const output = document.getElementById("chat-output");
  
    addUserMessage("📊 Compare these two videos");
  
    fetch("/compare-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: "Compare these two videos",
        transcript1: transcript1,
        transcript2: transcript2,
        is_first: true
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        addBotMessage(data.reply);
      })
      .catch(() => {
        addBotMessage("❌ Error occurred.");
      });
  }
  