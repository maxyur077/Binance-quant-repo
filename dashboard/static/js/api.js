async function fetchJSON(url) {
    try {
        var res = await fetch(url);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        return null;
    }
}

async function postJSON(url, body) {
    try {
        var res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        return await res.json();
    } catch (e) {
        return null;
    }
}
