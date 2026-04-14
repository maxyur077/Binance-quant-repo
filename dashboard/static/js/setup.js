var selectedMode = null;

function selectMode(mode) {
    selectedMode = mode;
    var dryCard = document.getElementById("dryRunCard");
    var liveCard = document.getElementById("liveCard");
    var dryRadio = document.getElementById("dryRadio");
    var liveRadio = document.getElementById("liveRadio");
    var apiSection = document.getElementById("apiKeySection");
    var startBtn = document.getElementById("startBtn");

    dryCard.classList.remove("border-warn/40", "bg-surface-600");
    liveCard.classList.remove("border-profit/40", "bg-surface-600");
    dryRadio.innerHTML = "";
    liveRadio.innerHTML = "";

    if (mode === "dry_run") {
        dryCard.classList.add("border-warn/40", "bg-surface-600");
        dryRadio.innerHTML = '<div class="w-2.5 h-2.5 rounded-full bg-warn mx-auto mt-[3px]"></div>';
        dryRadio.classList.add("border-warn");
        liveRadio.classList.remove("border-profit");
        apiSection.classList.add("hidden");
    } else {
        liveCard.classList.add("border-profit/40", "bg-surface-600");
        liveRadio.innerHTML = '<div class="w-2.5 h-2.5 rounded-full bg-profit mx-auto mt-[3px]"></div>';
        liveRadio.classList.add("border-profit");
        dryRadio.classList.remove("border-warn");
        apiSection.classList.remove("hidden");
    }

    startBtn.disabled = false;
}

async function submitSetup() {
    if (!selectedMode) return;

    var startBtn = document.getElementById("startBtn");
    var errorEl = document.getElementById("setupError");
    errorEl.classList.add("hidden");
    startBtn.disabled = true;
    startBtn.textContent = "Starting...";

    var payload = { mode: selectedMode };

    if (selectedMode === "live") {
        var apiKey = document.getElementById("apiKeyInput").value.trim();
        var apiSecret = document.getElementById("apiSecretInput").value.trim();
        if (!apiKey || !apiSecret) {
            errorEl.textContent = "API Key and Secret are required for live trading.";
            errorEl.classList.remove("hidden");
            startBtn.disabled = false;
            startBtn.textContent = "Start Trading";
            return;
        }
        payload.api_key = apiKey;
        payload.api_secret = apiSecret;
    }

    try {
        var res = await fetch("/setup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        var data = await res.json();
        if (data.success) {
            window.location.href = "/";
        } else {
            errorEl.textContent = data.error || "Setup failed.";
            errorEl.classList.remove("hidden");
            startBtn.disabled = false;
            startBtn.textContent = "Start Trading";
        }
    } catch (e) {
        errorEl.textContent = "Network error. Please try again.";
        errorEl.classList.remove("hidden");
        startBtn.disabled = false;
        startBtn.textContent = "Start Trading";
    }
}
