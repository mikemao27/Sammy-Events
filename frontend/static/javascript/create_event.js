document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("create-event-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const title = document.getElementById("title").value.trim();
        const description = document.getElementById("description").value.trim();
        const start_time = document.getElementById("start_time").value.trim();
        const end_time = document.getElementById("end_time").value.trim();
        const location = document.getElementById("location").value.trim();
        const organization_name =
            document.getElementById("organization_name").value.trim();
        const free_food = document.getElementById("free_food").checked;

        if (!title) {
            alert("Title is required.");
            return;
        }

        const response = await fetch("/api/events/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                title,
                description,
                start_time,
                end_time,
                location,
                organization_name,
                free_food,
            }),
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.ok === false) {
            alert(data.error || "Failed to Create Event");
            return;
        }

        alert("Event Created!");
        window.location.href = "events.html";
    });
});
