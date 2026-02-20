const boardEl = document.getElementById("board");
const overlayEl = document.getElementById("colOverlay");
const statusEl = document.getElementById("status");
const resetBtn = document.getElementById("resetBtn");

let locked = false; // prevent double taps while CPU responds

function setStatus(text) {
  statusEl.textContent = text;
}

function renderGrid(grid) {
  boardEl.innerHTML = "";
  // grid is 6 rows x 7 cols, row 0 is top
  for (let r = 0; r < 6; r++) {
    for (let c = 0; c < 7; c++) {
      const v = grid[r][c];
      const cell = document.createElement("div");
      cell.className = "cell";
      if (v === "X") cell.classList.add("player");
      if (v === "O") cell.classList.add("cpu");
      boardEl.appendChild(cell);
    }
  }
}

function renderOverlay(validMoves, winner) {
  overlayEl.innerHTML = "";
  for (let c = 0; c < 7; c++) {
    const hit = document.createElement("div");
    hit.className = "colHit";

    const enabled = winner === null && validMoves.includes(c) && !locked;
    hit.style.opacity = enabled ? "1" : "0.25";
    hit.style.cursor = enabled ? "pointer" : "not-allowed";

    if (enabled) {
      hit.addEventListener("click", () => playMove(c));
      hit.addEventListener("touchstart", (e) => {
        e.preventDefault();
        playMove(c);
      }, { passive: false });
    }

    overlayEl.appendChild(hit);
  }
}

function winnerText(winner) {
  if (winner === "PLAYER") return "You win! 🎉";
  if (winner === "CPU") return "CPU wins. 🤖";
  if (winner === "DRAW") return "Draw.";
  return null;
}

async function fetchState() {
  const res = await fetch("/api/state");
  const data = await res.json();
  updateFromState(data);
}

function updateFromState(data) {
  renderGrid(data.grid);

  const wtxt = winnerText(data.winner);
  if (wtxt) {
    setStatus(wtxt + "  (Press Reset to play again)");
  } else {
    setStatus("Your turn: click a column.");
  }

  renderOverlay(data.valid_moves, data.winner);
}

async function playMove(col) {
  if (locked) return;
  locked = true;
  setStatus("Thinking…");
  renderOverlay([], null); // visually disable inputs

  try {
    const res = await fetch("/api/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ col })
    });

    const data = await res.json();

    if (!res.ok) {
      setStatus(data.error || "Invalid move.");
      locked = false;
      await fetchState();
      return;
    }

    updateFromState(data);
  } catch (e) {
    setStatus("Network error. Try again.");
    await fetchState();
  } finally {
    locked = false;
    // re-render overlay in case it was disabled
    await fetchState();
  }
}

resetBtn.addEventListener("click", async () => {
  locked = true;
  setStatus("Resetting…");
  try {
    const res = await fetch("/api/reset", { method: "POST" });
    const data = await res.json();
    updateFromState(data);
  } finally {
    locked = false;
    await fetchState();
  }
});

// initial load
fetchState();