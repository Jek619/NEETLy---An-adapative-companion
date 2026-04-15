const fs = require("fs");
const SYLLABUS = require("./neet_topics_data");
const THEORY = require("./theory_templates");

let notes = {};

Object.keys(SYLLABUS).forEach(subject => {
  notes[subject] = {};

  Object.values(SYLLABUS[subject]).flat().forEach(topic => {
    notes[subject][topic] = {
      full: THEORY[subject](topic),

      key_points: [
        `Important chapter from ${subject}`,
        "NCERT-based concepts",
        "Frequently asked in NEET",
        "Concept clarity is essential"
      ],

      definitions: [
        `${topic}: Definition as per NCERT`,
        "Important scientific terms related to this chapter"
      ],

      pyqs: [
        `NEET: Conceptual question from ${topic}`,
        `NEET: Assertion–Reason question`
      ],

      revision: [
        "Important formulas / facts",
        "NCERT diagrams",
        "Exam-oriented points"
      ]
    };
  });
});

fs.writeFileSync("notes.json", JSON.stringify(notes, null, 2));
console.log("✅ TOPIC-SPECIFIC DETAILED THEORY GENERATED");
