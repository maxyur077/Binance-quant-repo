function renderEquityChart(canvasId, data) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    var emptyEl = document.getElementById("chartEmpty");

    if (!data || data.length === 0) {
        if (emptyEl) emptyEl.style.display = "block";
        return;
    }
    if (emptyEl) emptyEl.style.display = "none";

    var ctx = canvas.getContext("2d");
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = (rect.height - 32) * dpr;
    canvas.style.width = rect.width + "px";
    canvas.style.height = (rect.height - 32) + "px";
    ctx.scale(dpr, dpr);

    var w = rect.width;
    var h = rect.height - 32;
    var pad = { top: 20, right: 16, bottom: 30, left: 60 };
    var chartW = w - pad.left - pad.right;
    var chartH = h - pad.top - pad.bottom;

    var values = data.map(function (d) { return d.balance; });
    var rawMin = Math.min.apply(null, values);
    var rawMax = Math.max.apply(null, values);
    var rawRange = rawMax - rawMin;
    var minPad = Math.max(rawMin * 0.002, 1);
    var minV = rawRange < 0.01 ? rawMin - minPad : rawMin - rawRange * 0.05;
    var maxV = rawRange < 0.01 ? rawMax + minPad : rawMax + rawRange * 0.05;
    var rangeV = maxV - minV || 1;

    function xPos(i) { return pad.left + (i / (data.length - 1 || 1)) * chartW; }
    function yPos(v) { return pad.top + (1 - (v - minV) / rangeV) * chartH; }

    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(255,255,255,0.04)";
    ctx.lineWidth = 1;
    for (var gi = 0; gi <= 4; gi++) {
        var gy = pad.top + (gi / 4) * chartH;
        ctx.beginPath();
        ctx.moveTo(pad.left, gy);
        ctx.lineTo(w - pad.right, gy);
        ctx.stroke();

        var gv = maxV - (gi / 4) * rangeV;
        ctx.fillStyle = "rgba(255,255,255,0.25)";
        ctx.font = "11px 'JetBrains Mono'";
        ctx.textAlign = "right";
        ctx.fillText("$" + gv.toFixed(0), pad.left - 8, gy + 4);
    }

    var grad = ctx.createLinearGradient(0, pad.top, 0, h - pad.bottom);
    var lastVal = values[values.length - 1];
    var firstVal = values[0];
    if (lastVal >= firstVal) {
        grad.addColorStop(0, "rgba(16,185,129,0.2)");
        grad.addColorStop(1, "rgba(16,185,129,0)");
    } else {
        grad.addColorStop(0, "rgba(239,68,68,0.2)");
        grad.addColorStop(1, "rgba(239,68,68,0)");
    }

    ctx.beginPath();
    ctx.moveTo(xPos(0), h - pad.bottom);
    for (var fi = 0; fi < data.length; fi++) {
        ctx.lineTo(xPos(fi), yPos(values[fi]));
    }
    ctx.lineTo(xPos(data.length - 1), h - pad.bottom);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.beginPath();
    for (var li = 0; li < data.length; li++) {
        if (li === 0) ctx.moveTo(xPos(li), yPos(values[li]));
        else ctx.lineTo(xPos(li), yPos(values[li]));
    }
    ctx.strokeStyle = lastVal >= firstVal ? "#10b981" : "#ef4444";
    ctx.lineWidth = 2;
    ctx.lineJoin = "round";
    ctx.stroke();

    var lastX = xPos(data.length - 1);
    var lastY = yPos(lastVal);
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fillStyle = lastVal >= firstVal ? "#10b981" : "#ef4444";
    ctx.fill();
    ctx.beginPath();
    ctx.arc(lastX, lastY, 7, 0, Math.PI * 2);
    ctx.strokeStyle = lastVal >= firstVal ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)";
    ctx.lineWidth = 2;
    ctx.stroke();
}
