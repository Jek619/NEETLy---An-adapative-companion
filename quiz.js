// ----------------------------
// NEETly – REAL EXAM MODE QUIZ SYSTEM
// ----------------------------

const API = "http://127.0.0.1:8000";

// DOM Elements
const subjectSelect = document.getElementById("subjectSelect");
const topicSelect = document.getElementById("topicSelect");
const difficultySelect = document.getElementById("difficultySelect");
const generateBtn = document.getElementById("generateQuiz");
const chooseNone = document.getElementById("chooseNone");
const quizContainer = document.getElementById("quizContainer");

async function saveQuizResultToDB(result) {
    if (!window.CURRENT_USER || !window.sb) {
        console.error("Auth or Supabase not ready");
        return;
    }

    const { error } = await window.sb
        .from("quiz_results")
        .insert([
            {
                user_id: window.CURRENT_USER.id,
                topic_id: result.topic,
                correct: result.correct,
                total: result.total,
                percent: Math.round(result.percentage)
            }
        ]);

    if (error) {
        console.error("Supabase insert failed:", error);
    } else {
        console.log("Quiz result saved to Supabase ✔");
    }
}



// Create Submit Button dynamically
let submitBtn = document.createElement("button");
submitBtn.id = "submitQuiz";
submitBtn.textContent = "Submit Quiz 📝";
submitBtn.className = "submit-btn hidden";
submitBtn.style = `
    background:#28a745;
    color:white;
    padding:15px;
    border-radius:10px;
    width:100%;
    font-size:18px;
    margin-top:15px;
    cursor:pointer;
`;
document.getElementById("quizTab").appendChild(submitBtn);

let topics = [];
let currentQuestions = [];

// ---------------------------------------------------
// LOAD TOPICS FROM JSON FILES (physics.json etc.)
// ---------------------------------------------------
async function loadTopics() {
    const subject = subjectSelect.value.toLowerCase();

    topicSelect.innerHTML = `<option>Loading topics...</option>`;

    try {
        const res = await fetch(`${subject}.json`);

        if (!res.ok) throw new Error("JSON not found: " + subject);

        const data = await res.json();

        topics = Object.keys(data);

        topicSelect.innerHTML = topics.length
            ? `<option value="">Select Topic</option>`
            : `<option>No topics found</option>`;

        topics.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t;
            opt.textContent = t;
            topicSelect.appendChild(opt);
        });

    } catch (err) {
        console.error("Error loading topics", err);
        topicSelect.innerHTML = `<option>Error loading topics</option>`;
    }
}

loadTopics();
subjectSelect.addEventListener("change", loadTopics);

// ---------------------------------------------------
// RANDOM TOPIC SELECTOR
// ---------------------------------------------------
chooseNone.addEventListener("click", () => {
    if (!topics.length) return alert("Topics not loaded!");
    topicSelect.value = topics[Math.floor(Math.random() * topics.length)];
});

// ---------------------------------------------------
// GENERATE QUIZ FROM BACKEND
// ---------------------------------------------------
generateBtn.addEventListener("click", async () => {
    const subject = subjectSelect.value;
    const topic = topicSelect.value;
    const difficulty = difficultySelect.value;

    if (!topic) return alert("Choose a topic!");

    quizContainer.innerHTML = `<p>⏳ Generating quiz...</p>`;
    submitBtn.classList.add("hidden");

    try {
        const res = await fetch(
            `${API}/quiz?subject=${subject}&topic=${topic}&difficulty=${difficulty}`
        );

        const data = await res.json();

        if (!data.questions || !data.questions.length) {
            quizContainer.innerHTML = `<p>No questions found.</p>`;
            return;
        }

        currentQuestions = data.questions;
        displayQuestions(currentQuestions);

    } catch (err) {
        console.error("Quiz Error:", err);
        quizContainer.innerHTML = `<p style="color:red;">Error generating quiz</p>`;
    }
});

// ---------------------------------------------------
// DISPLAY QUESTIONS
// ---------------------------------------------------
function displayQuestions(questions) {
    quizContainer.innerHTML = "";
    submitBtn.classList.remove("hidden");

    questions.forEach((q, i) => {
        const card = document.createElement("div");
        card.className = "question-card fade";

        card.innerHTML = `
            <h3>Q${i + 1}. ${q.question}</h3>
            ${q.options
                .map(
                    opt => `
                <label style="display:block; margin:6px 0;">
                    <input type="radio" name="q${i}" value="${opt}">
                    ${opt}
                </label>
            `
                )
                .join("")}

            <div id="review-${i}" class="hidden"></div>
        `;

        quizContainer.appendChild(card);
    });
}

// ---------------------------------------------------
// SUBMIT QUIZ + REVIEW MODE
// ---------------------------------------------------
submitBtn.addEventListener("click", async () => {

    let correct = 0;
    let wrong = 0;

    currentQuestions.forEach((q, i) => {
        const selected = document.querySelector(`input[name="q${i}"]:checked`);
        if (selected && selected.value === q.answer) correct++;
        else wrong++;
    });

    const total = currentQuestions.length;
    const percentage = Math.round((correct / total) * 100);

    // -----------------------------------
    // BUILD RESULT OBJECT
    // -----------------------------------
    let result = {
        subject: subjectSelect.value,
        topic: topicSelect.value,
        correct: correct,
        wrong: wrong,
        total: total,
        percentage: percentage,
        difficulty: difficultySelect.value,
        timestamp: new Date().toLocaleString(),
    };
    // SAVE TO SUPABASE
    await saveQuizResultToDB(result);



    // -----------------------------------
    // SAVE LATEST RESULT FOR DASHBOARD
    // -----------------------------------
    localStorage.setItem("latestQuizResult", JSON.stringify(result));

    // -----------------------------------
    // SAVE FULL QUIZ HISTORY (FIXED)
    // -----------------------------------
    let history = JSON.parse(localStorage.getItem("quizHistory") || "[]");
    history.push(result);
    localStorage.setItem("quizHistory", JSON.stringify(history));

    // -----------------------------------
    // SCORE SUMMARY UI
    // -----------------------------------
    const scoreBox = document.createElement("div");
    scoreBox.className = "score-box";
    scoreBox.innerHTML = `
        <h2>🎯 Quiz Summary</h2>
        <h3>Score: <span style="color:lightgreen;">${correct}/${total}</span></h3>
        <h3>Percentage: <span style="color:#4db8ff;">${percentage}%</span></h3>
    `;
    quizContainer.prepend(scoreBox);

    // -----------------------------------
    // PER-QUESTION REVIEW
    // -----------------------------------
    currentQuestions.forEach((q, i) => {
        const selected = document.querySelector(`input[name="q${i}"]:checked`);
        const userAnswer = selected ? selected.value : null;

        const reviewBox = document.getElementById(`review-${i}`);
        reviewBox.classList.remove("hidden");

        let correctOption = q.answer;
        let explanation = q.explanation || "No explanation provided.";

        reviewBox.innerHTML = `
            <p><strong>Your Answer:</strong>
                <span style="color:${userAnswer === correctOption ? "lightgreen" : "red"};">
                    ${userAnswer || "Not attempted"}
                </span>
            </p>
            <p><strong>Correct Answer:</strong>
                <span style="color:lightgreen;">${correctOption}</span>
            </p>
            <p><strong>Explanation:</strong> ${explanation}</p>
        `;

        document.querySelectorAll(`input[name="q${i}"]`).forEach(opt => {
            if (opt.value === correctOption) {
                opt.parentElement.style.color = "lightgreen";
                opt.parentElement.style.fontWeight = "600";
            }
            if (userAnswer && opt.value === userAnswer && userAnswer !== correctOption) {
                opt.parentElement.style.color = "red";
                opt.parentElement.style.fontWeight = "600";
            }
        });
    });

    submitBtn.disabled = true;
    submitBtn.textContent = "Quiz Completed 🎉";
});

console.log("NEETly Real Exam Mode Loaded ✔");
