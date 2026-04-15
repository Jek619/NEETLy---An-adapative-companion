// =====================
// LOAD USER NAME
// =====================

const welcomeUser = document.getElementById("welcomeUser");

let storedUser =
  localStorage.getItem("username") ||
  localStorage.getItem("user") ||
  localStorage.getItem("name");

if (!storedUser) {
  storedUser = "ANAGHA PK"; // fallback
}

if (welcomeUser) {
  welcomeUser.innerText = storedUser.toUpperCase();
}


// =====================
// ELEMENTS
// =====================

const subjectSelect = document.getElementById("subjectSelect");
const topicSelect = document.getElementById("topicSelect");
const notesContent = document.getElementById("notesContent");
const notesHeader = document.getElementById("notesHeader");
const viewNotesBtn = document.getElementById("viewNotesBtn");


// =====================
// LOAD SUBJECTS
// =====================

function loadSubjects() {
  subjectSelect.innerHTML = `<option value="">Select Subject</option>`;

  Object.keys(NEET_TOPICS).forEach(subject => {
    subjectSelect.innerHTML += `<option value="${subject}">${subject}</option>`;
  });
}


// =====================
// SUBJECT CHANGE
// =====================

subjectSelect.addEventListener("change", () => {

  const subject = subjectSelect.value;

  topicSelect.innerHTML = `<option value="">Select Topic</option>`;
  notesContent.innerHTML = "Please select a topic.";
  notesHeader.innerText = "Key Points";
  viewNotesBtn.disabled = true;

  if (!subject) return;

  NEET_TOPICS[subject].forEach(topic => {
    topicSelect.innerHTML += `<option value="${topic}">${topic}</option>`;
  });

});


// =====================
// TOPIC CHANGE
// =====================

topicSelect.addEventListener("change", () => {
  loadNote();
  toggleNotesButton();
});


// =====================
// ENABLE VIEW BUTTON
// =====================

function toggleNotesButton() {

  const subject = subjectSelect.value;
  const topic = topicSelect.value;

  if (window.NOTES_PDF?.[subject]?.[topic]) {
    viewNotesBtn.disabled = false;
  } else {
    viewNotesBtn.disabled = true;
  }
}


// =====================
// VIEW NOTES (DOWNLOAD DIRECTLY)
// =====================

viewNotesBtn.addEventListener("click", () => {

  const subject = subjectSelect.value;
  const topic = topicSelect.value;

  const pdfUrl = window.NOTES_PDF?.[subject]?.[topic];

  if (!pdfUrl) {
    alert("Notes not available for this topic.");
    return;
  }

  // 👉 force download
  const link = document.createElement("a");
  link.href = pdfUrl;
  link.download = topic + ".pdf";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
});


// =====================
// LOAD NOTES CONTENT
// =====================

function loadNote() {

  const subject = subjectSelect.value;
  const topic = topicSelect.value;

  if (!subject || !topic) {
    notesContent.innerHTML = "Please select subject and topic.";
    return;
  }

  const keyPoints = window.NEET_NOTES?.[subject]?.[topic]?.key_points;

  notesHeader.innerText = `${topic} — Key Points`;

  let contentHTML = "";


  // =====================
  // KEY POINTS
  // =====================

  if (keyPoints && keyPoints.length > 0) {
    contentHTML += `
      <ul class="note-list">
        ${keyPoints.map(point => `<li>${point}</li>`).join("")}
      </ul>
    `;
  } else {
    contentHTML += `<p>No key points available.</p>`;
  }


  // =====================
  // DOWNLOAD BUTTON (MAIN)
  // =====================

  const pdfUrl = window.NOTES_PDF?.[subject]?.[topic];

  if (pdfUrl) {
    contentHTML += `
      <div style="margin-top:20px;">
        <a href="${pdfUrl}" download class="btn">
          ⬇ Download Notes
        </a>
      </div>
    `;
  }


  // =====================
  // NCERT BUTTON
  // =====================

  if (window.NCERT_LINKS?.[subject]) {
    contentHTML += `
      <div style="margin-top:15px;">
        <a href="https://ncert.nic.in/textbook.php" target="_blank" class="btn">
          📚 Open NCERT Books
        </a>
      </div>
    `;
  }


  // =====================
  // FINAL RENDER
  // =====================

  notesContent.innerHTML = contentHTML;
}


// =====================
// INIT
// =====================

loadSubjects();