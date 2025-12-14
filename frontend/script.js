const API_BASE = "http://127.0.0.1:8000/api"; // Backend base URL with prefix

document.getElementById("resumeForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = document.getElementById("file").files[0];
    const keyword = document.getElementById("keyword").value.trim();
    const location = document.getElementById("location").value.trim();
    const loading = document.getElementById("loading");
    const resultsDiv = document.getElementById("results");

    if (!file) {
        alert("Please upload a resume file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("keyword", keyword);
    formData.append("location", location);

    loading.classList.remove("hidden");
    resultsDiv.innerHTML = "";

    try {
        const res = await fetch(`${API_BASE}/resume-jobs`, {
    method: "POST",
    body: formData
});

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        console.log("API Response:", data);

        loading.classList.add("hidden");

        if (!data.jobs || data.jobs.length === 0) {
            resultsDiv.innerHTML = "<p>No jobs found. Try another keyword or location.</p>";
            return;
        }

        data.jobs.forEach(job => {
            const card = document.createElement("div");
            card.classList.add("job-card");

            card.innerHTML = `
                <h3>${job.title}</h3>
                <p><strong>Company:</strong> ${job.company}</p>
                <p><strong>Location:</strong> ${job.location}</p>
                <p>${job.description || "No description available."}</p>
                <a href="${job.apply_link || "#"}" target="_blank">Apply Here</a>
            `;
            resultsDiv.appendChild(card);
        });

    } catch (err) {
        loading.classList.add("hidden");
        resultsDiv.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
    }
});
