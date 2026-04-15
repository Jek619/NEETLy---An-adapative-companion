// Simple admin protection
const isAdmin = localStorage.getItem("isAdmin");

if (isAdmin !== "true") {
    alert("Access Denied!");
    window.location.href = "dashboard.html";
}

// Add quiz question
function addQuestion() {
    let question = document.getElementById("question").value;
    let option1 = document.getElementById("option1").value;
    let option2 = document.getElementById("option2").value;
    let option3 = document.getElementById("option3").value;
    let option4 = document.getElementById("option4").value;
    let answer = document.getElementById("answer").value;

    let newQuestion = {
        question,
        options: [option1, option2, option3, option4],
        answer
    };

    let questions = JSON.parse(localStorage.getItem("questions")) || [];
    questions.push(newQuestion);

    localStorage.setItem("questions", JSON.stringify(questions));

    alert("Question Added Successfully!");
}

// Add note
function addNote() {
    let note = document.getElementById("note").value;

    let notes = JSON.parse(localStorage.getItem("notes")) || [];
    notes.push(note);

    localStorage.setItem("notes", JSON.stringify(notes));

    alert("Note Added Successfully!");
}

const users = [
  { id: 1, name: "Jishnu", email: "jishnu@gmail.com", attempts: 3, average: 75 },
  { id: 2, name: "Arjun", email: "arjun@gmail.com", attempts: 5, average: 68 }
];

document.getElementById("totalUsers").innerText = users.length;