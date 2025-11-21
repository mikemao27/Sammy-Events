let allEvents = [];

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("events-list");
    const fieldSelect = document.getElementById("event-field-filter");
    const freeFoodToggle = document.getElementById("free-food-toggle");

    async function loadEvents() {
        container.textContent = "Loading Events...";

        try {
            const response = await fetch("/api/events", {credentials: "include"});
            if (!response.ok) throw new Error("Network Reponse Error");
            allEvents = await response.json();
            populateEventFieldFilter(allEvents, fieldSelect);
            renderFiltered();
        } catch (error) {
            console.error(error);
            container.textContent = "Failed to Load Events";
        }
    }

    function populateEventFieldFilter(events, selectElements) {
        const fields = new Set();
        events.forEach(event => {
            if (event.academic_fields) {
                event.academic_fields.split(",").forEach(field => fields.add(field.trim()));
            }
        });

        while (selectElements.options.length > 1) selectElements.remove(1);
        Array.from(fields).sort().forEach(field => {
            const option = document.createElement("option");
            option.value = field;
            option.textContent = field;
            selectElements.appendChild(option);
        });
    }

    function renderFiltered() {
        const field = fieldSelect.value;
        const freeFoodOnly = freeFoodToggle.checked;
        const container = document.getElementById("events-list");
        container.innerHTML = "";

        let events = allEvents.slice();

        if (field) {
            events = events.filter(event => 
                (event.academic_fields || "")
                    .split(",")
                    .map(s => s.trim())
                    .includes(field)
            );
        }

        if (freeFoodOnly) {
            events = event.filter(event => event.free_food === 1 || event.free_food === true);
        }

        if (events.length === 0) {
            container.textContent = "No Events Match This Filter";
            return;
        }

        const recommended = events.filter(event => event.followed === 1 || event.followed === true);
        const others = events.filter(event => !recommended.includes(event));

        if (recommended.length > 0) {
            const h2 = document.createElement("h2");
            h2.textContent = "Recommended for you";
            container.appendChild(h2);
            recommended.forEach(event => container.appendChild(renderEventCard(event)));
        }

        const h2all = document.createElement("h2");
        h2all.textContent = recommended.length ? "All Events" : "Events";
        container.appendChild(h2all);
        others.forEach(event => container.appendChild(renderEventCard(event)));
    }

    fieldSelect.addEventListener("Change", renderFiltered);
    freeFoodToggle.addEventListener("Change", renderFiltered);

    await loadEvents();
});

function renderEventCard(event) {
    const card = document.createElement("div");
    card.className = "card";

    const start = event.start_time ? new Date(event.start_time).toLocaleString() : "Time TBD";
    const location = event.event_location || "Location TBD";
    const description = event.event_description || "";
    const organization = event.organization_name || "";

    card.innerHTML = `
        <div class = "card-header">
            <div>
                <div class = "card-title">${event.title}</div>
                <div class = "card-meta">${start} - ${location}</div>
                ${organization ? `<div class = "card-meta">Hosted By ${organization}</div>` :  ""}
            </div>

            <div class = "card-meta">${event.source}</div>
        </div>

        <div class = "card-body">
            ${description}
            <div style = "margin-top: 8px;">
                <a class = "button" href = "${event.sourc_url}" target = "_blank" rel = "noopener">
                    View on Source Site
                </a>
            </div>
        </div>
    `;
    return card;
}