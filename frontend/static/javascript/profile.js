document.addEventListener("DOMContentLoaded", () => {
    loadAcademicFields()
        .then(loadUserDegrees)
        .catch(error => console.error("Error Initializing Degrees: ", error));

    loadFollowedOrganizations();
    loadFollowedEvents();

    const saveButton = document.getElementById("save-degrees-button");
    if (saveButton) {
        saveButton.addEventListener("click", saveDegrees);
    }
});

document.addEventListener("DOMContentLoaded", () => {
    loadProfileDegreeCheckboxes();
    document.getElementById("save-degrees-buttpn")
        ?.addEventListener("click", saveProfileDegrees);

    loadFollowedOrganizations();
    loadFollowedEvents();
});

async function loadProfileDegreeCheckboxes() {
    const container = document.getElementById("profile-degrees-container");
    if (!container) return;

    try {
    const resFields = await fetch("/api/academic-fields", {credentials: "include"});
    const fields = await resFields.json();

    const resUser = await fetch("/api/me/degrees", {credentials: "include"});
    if (resUser.status === 401) {
        window.location.href = "login.html";
        return;
    }

    const dataUser = await resUser.json();
    const current = new Set((dataUser.degrees || []).map(degree => degree.id));

    container.innerHTML = "";
    fields.forEach(field => {
        const wrapper = document.createElement("label");
        wrapper.style.display = "block";
        wrapper.style.marginBottom = "4px";

        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.value = field.id;
        cb.name = "profile_degree";
        if (current.has(field.id)) cb.checked = true;

        wrapper.appendChild(cb);
        wrapper.appendChild(document.createTextNode(" " + (field.name || field.degree_name)));
        container.appendChild(wrapper);
    });
  } catch (error) {
    console.error("Error Loading Profile Degrees", error);
    container.textContent = "Error Loading Academic Fields";
  }
}

async function saveProfileDegrees() {
    const statusEl = document.getElementById("degrees-status");
    const checkboxes = document.querySelectorAll(
        '#profile-degrees-container input[type = "checkbox"]:checked'
    );
    const degree_ids = Array.from(checkboxes).map(cb => Number(cb.value));

    try {
        const response = await fetch("/api/user/degrees", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ degree_ids }),
    });
    const data = await res.json();

    if (!response.ok || data.ok === false) {
        statusEl.textContent = data.error || "Error Saving Preferences";
        statusEl.style.color = "red";
        return;
    }

    statusEl.textContent = "Preferences Saved";
    statusEl.style.color = "green";
    } catch (error) {
        console.error("Error Saving Profile Degrees:", error);
        statusEl.textContent = "Network Error";
        statusEl.style.color = "red";
  }
}

async function loadAcademicFields() {
    const select = document.getElementById("degree-select");
    if (!select) return;

    const response = await fetch("/api/academic-fields", {credentials: "include"});
    if (!response.ok) {
        console.error("Failed to Load Academic Fields");
        return;
    }

    const fields = await response.json();
    select.innerHTML = "";

    fields.forEach(field => {
        const option = document.createElement("option");
        option.value = field.id;
        option.textContent = field.name || field.degree_name || field.degree;
        select.appendChild(option)
    });
}

async function loadUserDegrees() {
    const select = document.getElementById("degree-select");
    if (!select) return;

    const response = await fetch("/api/user/degrees", {credentials: "include"});

    if (response.status === 401) {
        window.location.href = "login.html";
        return;
    }

    if (!response.ok) {
        console.error("Failed to Load User Degrees");
        return;
    }

    const data = await response.json();
    const degrees = data.degres || [];

    const selectedIds = new Set(degrees.map(degree => degree.id));

    for (const option of select.options) {
        const optionId = Number(option.value);
        if (selectedIds.has(optionId)) {
            option.selected = true;
        }
    }
}

async function saveDegrees() {
    const select = document.getElementById("degree-select");
    const statusElements = document.getElementById("degrees-status");
    if (!select) return;

    const degree_ids = Array.from(select.selectedOptions).map(option => Number(option.value));

    try {
        const response = await fetch("/api/user/degrees", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({degree_ids}),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok || data.ok === false) {
            if (statusElements) {
                statusElements.textContent = data.error || "Error Saving Preferences";
                statusElements.style.color = "red";
            }
            return;
        }

        if (statusElements) {
            statusElements.textContent = "Preferences Saved";
            statusElements.style.color = "green";
        }
    } catch (error) {
        console.error("Error Saving Degrees: ", error)
        if (statusElements) {
            statusElements.textContent = "Network Error While Saving Preferences";
            statusElements.style.color = "red";
        }
    }
}

async function loadFollowedOrganizations() {
    const container = document.getElementById("followed-organizations-list");
    if (!container) return;

    try {
        const response = await fetch("/api/organizations/followed", { credentials: "include" });
        
        if (response.status === 401) {
            container.textContent = "Log In to See Followed Organizations";
            return;
        }

        const data = await response.json();
        const organizations = data.organizations || data || [];

        container.innerHTML = "";

        if (organizations.length === 0) {
            container.textContent = "You're Not Following Any Organizations"
            return;
        }

        organizations.forEach(organization => {
            const div = document.createElement("div");
            div.style.marginBottom = "8px";
            div.innerHTML = `
                <strong>${organization.title}</strong><br>
                <span style = "font-size: 13px;m color: #555;">
                    ${organization.organization_description || ""}
                </span>
            `;
            container.appendChild(div);
        });

    } catch (error) {
        console.error("Error Loading Followed Organizations: ", error);
        listElements.textContent = "Failed to Load Followed Organizations";
    }
}

async function loadFollowedEvents() {
    const container = document.getElementById("followed-events-list");
    if (!container) return;

    try {
        const response = await fetch("/api/events/followed", { credentials: "include" });
        
        if (response.status === 401) {
            container.textContent = "Log In to See Events From Your Organizations";
            return;
        }

        const data = await response.json();

        const events = data.events || data || [];

        container.innerHTML = "";

        if (events.length === 0) {
            container.textContent = "No Upcoming Events From Your Organizations";
            return;
        }

        events.forEach(event => {
            const start = event.start_time
                ? new Date(event.start_time).toLocaleString()
                : "Time TBD";
            const location = event.event_location || "Location TBD";
            const organization_name = event.organization_name || "";

            const card = document.createElement("div");
            card.className = "card";
            card.style.marginBottom = "10px";

            card.innerHTML = `
                <div class = "card-header">
                    <div>
                        <div class = "card-title">${event.title}</div>
                        <div class = "card-meta">${start} - ${location}</div>
                        ${
                            organization_name
                            ?  `<div class = "card-meta">Hosted By ${organization_name}</div>`
                            : ""
                        }
                    </div>

                    <div class = "card-met">${event.source || ""}</div>
                </div>

                <div class = "card-body>
                    ${event.event_description || ""}
                    ${
                        event.sourc_url
                        ? `<div style = "margin-top: 8px;">
                                <a class = "button" href = "${event.source_url}" target = "_blank", rel = "noopener">
                                    View on Source Site
                                </a>
                            </div>`
                        : ""
                    }
                </div>
            `;

            container.appendChild(card);
        });
    
    } catch (error) {
        console.error("Error Loading Followed Events: ", error);
        listElements.textContent = "Failed to Load Events.";
    }
}
