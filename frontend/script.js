const API = "http://127.0.0.1:8000";

let chart;

// ---------------- UPLOAD ----------------
async function uploadResume() {
    let file = document.getElementById("resume").files[0];

    if (!file) {
        alert("Please select a resume first");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    try {
        let res = await fetch(API + "/upload", {
            method: "POST",
            body: formData
        });

        let data = await res.json();

        document.getElementById("output").innerText =
            data.message || "Resume Uploaded";

        document.getElementById("progress").style.width = "0%";

    } catch (err) {
        document.getElementById("output").innerText = "Upload Error";
        console.log(err);
    }
}

// ---------------- GRAPH ----------------
function showChart(score) {
    let ctx = document.getElementById("scoreChart").getContext("2d");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Score"],
            datasets: [{
                label: "Percentage",
                data: [score],
                borderWidth: 1
            }]
        }
    });
}

// ---------------- MATCH ----------------
async function getMatch() {
    let jd = document.getElementById("jd").value;

    if (jd.trim() === "") {
        alert("Enter Job Description");
        return;
    }

    try {
        let res = await fetch(API + "/match", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ job_description: jd })
        });

        let data = await res.json();

        if (data.error) {
            document.getElementById("output").innerText = data.error;
        } else {
            document.getElementById("output").innerText =
                "Match Score: " + data.score + "%";

            document.getElementById("progress").style.width =
                data.score + "%";

            showChart(data.score);
        }

    } catch (err) {
        document.getElementById("output").innerText = "Match Error";
        console.log(err);
    }
}

// ---------------- EVALUATE ----------------
async function evaluateAnswer() {
    let ans = document.getElementById("answer").value;

    if (ans.trim() === "") {
        alert("Enter Answer");
        return;
    }

    try {
        let res = await fetch(API + "/evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ answer: ans })
        });

        let data = await res.json();

        if (data.error) {
            document.getElementById("output").innerText = data.error;
        } else {
            document.getElementById("output").innerText =
                "Score: " + data.score + "/10 | " + data.result;

            document.getElementById("progress").style.width =
                (data.score * 10) + "%";

            showChart(data.score * 10);
        }

    } catch (err) {
        document.getElementById("output").innerText = "Evaluate Error";
        console.log(err);
    }
}

// ---------------- ATS ----------------
async function getATS() {
    let jd = document.getElementById("jd").value;

    if (jd.trim() === "") {
        alert("Enter Job Description");
        return;
    }

    try {
        let res = await fetch(API + "/ats-score", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ job_description: jd })
        });

        let data = await res.json();

        if (data.error) {
            document.getElementById("output").innerText = data.error;
        } else {
            document.getElementById("output").innerText =
                "ATS Score: " + data.ats_score + "/100\n" +
                "Matched Skills: " + data.matched_skills + "/" + data.total_skills +
                "\nSuggestions:\n- " + data.suggestions.join("\n- ");

            document.getElementById("progress").style.width =
                data.ats_score + "%";

            showChart(data.ats_score);
        }

    } catch (err) {
        document.getElementById("output").innerText = "ATS Error";
        console.log(err);
    }
}

// ---------------- DOWNLOAD ----------------
function downloadReport() {
    let content = document.getElementById("output").innerText;

    let blob = new Blob([content], { type: "text/plain" });
    let link = document.createElement("a");

    link.href = URL.createObjectURL(blob);
    link.download = "IntelliHire_Report.txt";
    link.click();
}