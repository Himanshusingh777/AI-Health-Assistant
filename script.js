const log = document.getElementById("log");
const input = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const ttsToggle = document.getElementById("ttsToggle");

function appendMessage(text, who="bot", meta=null) {
  const wrap = document.createElement("div");
  wrap.className = "bubble";
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  wrap.appendChild(div);
  if (meta) {
    const m = document.createElement("div");
    m.className = "meta";
    m.textContent = meta;
    wrap.appendChild(m);
  }
  log.appendChild(wrap);
  log.scrollTop = log.scrollHeight;
}

async function ask(query){
  appendMessage(query, "user");
  const res = await fetch("/ask", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({query})
  });
  const data = await res.json();
  const meta = data.match ? `closest match: "${data.match}" (score ${data.score})` : null;
  appendMessage(data.answer, "bot", meta);
  if (ttsToggle.checked) speak(data.answer);
}

sendBtn.onclick = () => {
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  ask(q);
};
input.addEventListener("keydown", (e)=>{
  if (e.key === "Enter") sendBtn.click();
});

// Web Speech API: SpeechRecognition (Chrome)
let recognition;
try {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR) {
    recognition = new SR();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event)=>{
      const transcript = event.results[0][0].transcript;
      ask(transcript);
    };
    recognition.onerror = (e)=>{
      appendMessage("Speech recognition error: " + e.error, "bot");
    };
  }
} catch (e) {
  console.warn("SpeechRecognition not available", e);
}

micBtn.onmousedown = () => {
  if (!recognition) {
    appendMessage("Speech recognition not supported in this browser.", "bot");
    return;
  }
  recognition.start();
  document.getElementById("micLabel").textContent = "🎙️ Listening...";
};
micBtn.onmouseup = () => {
  if (recognition) {
    recognition.stop();
    document.getElementById("micLabel").textContent = "🎤 Speak";
  }
};
micBtn.onclick = () => { /* for tap devices */ };

// TTS
function speak(text){
  if (!("speechSynthesis" in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
}

appendMessage("Hi! Ask me something from the knowledge base or press 🎤 to speak.");