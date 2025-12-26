const backendBaseUrl = "http://127.0.0.1:8000"; // change when you deploy

const classLevelSelect = document.getElementById("classLevel");
const subjectSelect = document.getElementById("subject");
const chapterSelect = document.getElementById("chapter");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const chatWindow = document.getElementById("chatWindow");

// Same chapter lists as backend
const CHAPTERS = {
  "Maths": [
    "Commercial Mathematics",
    "Algebra",
    "Geometry",
    "Mensuration",
    "Trigonometry"
  ],
  "Physics": [
    "Force, Work, Power and Energy",
    "Light",
    "Sound",
    "Electricity and Magnetism",
    "Heat",
    "Modern Physics"
  ],
};

function populateChapters() {
  const subject = subjectSelect.value;
  chapterSelect.innerHTML = "";
  CHAPTERS[subject].forEach(ch => {
    const opt = document.createElement("option");
    opt.value = ch;
    opt.textContent = ch;
    chapterSelect.appendChild(opt);
  });
}

subjectSelect.addEventListener("change", populateChapters);

// Initial population
populateChapters();

function appendMessage(role, text, meta) {
  const row = document.createElement("div");
  row.classList.add("message-row", role);

  const bubble = document.createElement("div");
  bubble.classList.add("message-bubble");

  if (role === "bot" && meta) {
    const metaDiv = document.createElement("div");
    metaDiv.classList.add("meta-text");
    metaDiv.textContent = `${meta.class_level} • ${meta.subject} • ${meta.chapter}`;
    bubble.appendChild(metaDiv);
  }

  const p = document.createElement("div");
  p.innerText = text;
  bubble.appendChild(p);

  row.appendChild(bubble);
  chatWindow.appendChild(row);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;

  const classLevel = classLevelSelect.value;
  const subject = subjectSelect.value;
  const chapter = chapterSelect.value;

  // User message
  appendMessage("user", question);

  // Clear input
  questionInput.value = "";
  questionInput.disabled = true;
  sendBtn.disabled = true;
  sendBtn.textContent = "Thinking...";

  try {
    const response = await fetch(`${backendBaseUrl}/api/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        class_level: classLevel,
        subject: subject,
        chapter: chapter,
        question: question
      })
    });

    if (!response.ok) {
      const errData = await response.json();
      appendMessage("bot", `Error: ${errData.detail || "Something went wrong."}`);
    } else {
      const data = await response.json();
      appendMessage("bot", data.answer, data.meta);
    }
  } catch (err) {
    appendMessage("bot", "Network error. Please try again.");
  } finally {
    questionInput.disabled = false;
    sendBtn.disabled = false;
    sendBtn.textContent = "Ask";
    questionInput.focus();
  }
}

sendBtn.addEventListener("click", sendQuestion);

questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
});
