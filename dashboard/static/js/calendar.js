function setupCalendarModal() {
    var overlay = document.getElementById("calendarModalOverlay");
    var openBtn = document.getElementById("openCalendarModal");
    var closeBtn = document.getElementById("closeCalendarModal");
    var closeBtn2 = document.getElementById("closeCalendarBtn");

    function openModal() {
        overlay.classList.add("visible");
        buildCalendar();
    }

    function closeModal() {
        overlay.classList.remove("visible");
    }

    if (openBtn) openBtn.addEventListener("click", openModal);
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (closeBtn2) closeBtn2.addEventListener("click", closeModal);

    overlay.addEventListener("click", function (e) {
        if (e.target === overlay) closeModal();
    });
}

async function buildCalendar() {
    var trades = await fetchJSON("/api/trades/closed");
    if (!trades) return;

    var now = new Date();
    var currentMonth = now.getMonth();
    var currentYear = now.getFullYear();

    var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    document.getElementById("calendarMonthTitle").textContent = "🗓️ " + monthNames[currentMonth] + " " + currentYear;

    var monthlyPnl = 0;
    var monthlyWins = 0;
    var monthlyTotal = 0;
    var dailyPnls = {};

    trades.forEach(function (t) {
        var exitDate = new Date(t.exit_time);
        if (exitDate.getMonth() === currentMonth && exitDate.getFullYear() === currentYear) {
            var day = exitDate.getDate();
            var pnl = parseFloat(t.pnl_usd) || 0;

            if (!dailyPnls[day]) dailyPnls[day] = { pnl: 0, count: 0 };
            dailyPnls[day].pnl += pnl;
            dailyPnls[day].count += 1;

            monthlyPnl += pnl;
            monthlyTotal++;
            if (pnl > 0) monthlyWins++;
        }
    });

    var calPnlEl = document.getElementById("calMonthlyPnl");
    calPnlEl.textContent = formatUSD(monthlyPnl);
    calPnlEl.className = monthlyPnl >= 0 ? "mt-1 text-lg font-mono font-bold text-profit" : "mt-1 text-lg font-mono font-bold text-loss";

    document.getElementById("calTotalTrades").textContent = monthlyTotal;

    var winRate = monthlyTotal > 0 ? (monthlyWins / monthlyTotal) * 100 : 0;
    var wrEl = document.getElementById("calWinRate");
    wrEl.textContent = winRate.toFixed(1) + "%";
    wrEl.className = winRate >= 50 ? "mt-1 text-lg font-mono font-bold text-profit" : "mt-1 text-lg font-mono font-bold text-loss";

    var grid = document.getElementById("calendarGrid");
    var labels = Array.from(grid.querySelectorAll(".cal-label"));
    grid.innerHTML = "";
    labels.forEach(function (h) { grid.appendChild(h); });

    var firstDay = new Date(currentYear, currentMonth, 1).getDay();
    var daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    for (var i = 0; i < firstDay; i++) {
        var emptyEl = document.createElement("div");
        emptyEl.className = "cal-day opacity-0";
        grid.appendChild(emptyEl);
    }

    for (var d = 1; d <= daysInMonth; d++) {
        var dayEl = document.createElement("div");
        dayEl.className = "cal-day";

        var dateNum = document.createElement("span");
        dateNum.className = "date-num";
        dateNum.textContent = d;
        dayEl.appendChild(dateNum);

        if (dailyPnls[d]) {
            var p = dailyPnls[d].pnl;
            var pnlEl = document.createElement("span");
            pnlEl.className = "day-pnl";
            pnlEl.textContent = formatUSD(p);
            dayEl.appendChild(pnlEl);

            if (p > 0) dayEl.classList.add("win");
            else if (p < 0) dayEl.classList.add("loss");
        }

        grid.appendChild(dayEl);
    }
}
