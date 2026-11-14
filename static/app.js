const uploadForm = document.querySelector("#upload-form");
const searchForm = document.querySelector("#search-form");
const statusEl = document.querySelector("#status");
const answerEl = document.querySelector("#answer");
const matchesEl = document.querySelector("#matches");

function setStatus(message) {
  statusEl.textContent = message;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = document.querySelector("#file").files[0];
  if (!file) {
    setStatus("Choose a file first.");
    return;
  }

  const data = new FormData();
  data.append("file", file);
  setStatus("Uploading and indexing...");

  try {
    const response = await fetch("/documents/upload", {
      method: "POST",
      body: data,
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Upload failed");
    setStatus(`Indexed ${payload.chunks_indexed} chunks from ${payload.document.filename}.`);
  } catch (error) {
    setStatus(error.message);
  }
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = document.querySelector("#query").value.trim();
  if (!query) {
    setStatus("Type a question first.");
    return;
  }

  setStatus("Searching...");
  answerEl.classList.add("hidden");
  matchesEl.innerHTML = "";

  try {
    const response = await fetch("/search", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        query,
        limit: 5,
        generate_answer: document.querySelector("#generate-answer").checked,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Search failed");

    if (payload.answer) {
      answerEl.innerHTML = `<h2>Answer</h2><p>${escapeHtml(payload.answer)}</p>`;
      answerEl.classList.remove("hidden");
    }

    matchesEl.innerHTML = payload.results.map((match) => `
      <article class="match">
        <h3>${escapeHtml(match.filename)}</h3>
        <div class="meta">Score ${Number(match.score).toFixed(3)} · chunk ${match.chunk_index}</div>
        <p>${escapeHtml(match.content)}</p>
      </article>
    `).join("");

    setStatus(`Found ${payload.results.length} matching chunks.`);
  } catch (error) {
    setStatus(error.message);
  }
});
