document.addEventListener("DOMContentLoaded", () => {
    loadOrgFields();
    setupCreateOrgForm();
});

async function loadOrgFields() {
    const container = document.getElementById("org-fields-container");
    if (!container) return;

    try {
        const res = await fetch("/api/academic-fields", { credentials: "include" });
        const fields = await res.json();

        container.innerHTML = "";
        fields.forEach((field) => {
            const label = document.createElement("label");
            label.style.display = "block";
            const cb = document.createElement("input");
            cb.type = "checkbox";
            cb.value = field.id;
            label.appendChild(cb);
            label.appendChild(
                document.createTextNode(" " + (field.name || field.degree_name))
            );
            container.appendChild(label);
        });
    } catch {
        container.textContent = "Could not Load Fields";
    }
}

function setupCreateOrgForm() {
    const form = document.getElementById("create-org-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const title = document.getElementById("org_title").value.trim();
        const description = document
            .getElementById("org_description")
            .value.trim();
        const academic_field_ids = Array.from(
            document.querySelectorAll("#org-fields-container input:checked")
            ).map((cb) => Number(cb.value));

        if (!title) {
            alert("Organization Name is Required.");
            return;
        }

        const response = await fetch("/api/organizations/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ title, description, academic_field_ids }),
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.ok === false) {
            alert(data.error || "Failed to Create Organization");
            return;
        }

        alert("Organization Created!");
        window.location.href = "organizations.html";
    });
}
