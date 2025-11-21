document.addEventListener("DOMContentLoaded", async () => {
    const listElements = document.getElementById("organizations_list")
    const filterElements = document.getElementById("field-filter")

    let allOrganizations = [];

    async function loadOrganizations() {
        listElements.textContent = "Loading Organizations...";
        try {
            const response = await fetch("/api/organizations", {credentials: "include"});
            if (!response.ok) throw new Error("Network Response Error");
            const organizations = await response.json();

            allOrganizations = organizations;
            populateFieldFilter(organizations);
            renderOrganizations(organizations);
        } catch (error) {
            console.error(error);
            listElements.textContent = "Failed to Load Organizations";
        }
    }

    function populateFieldFilter(organizations) {
        const fields = new Set();
        organizations.forEach(organization => {
            if (organization.academic_fields) {
                organization.academic_fields.split(",").forEach(field => {
                    const trimmed = field.trim();
                    if (trimmed) fields.add(trimmed)
                });
            }
        });

        while (filterElements.options.length > 1) {
            filterElements.remove(1);
        }

        Array.from(fields).sort().forEach(field => {
            const option = document.createElement("option");
            option.value = field;
            option.textContent = field;
            filterElements.appendChild(option);
        });
    }

    function attachFollowHandlers() {
        const buttons = document.querySelectorAll(".follow-button");
        buttons.forEach(button => {
            button.onclick = async () => {
                const organizationName = button.getAttribute("data-organization-name");
                const currentlyUnfollow = button.textContent.trim() === "Unfollow";
                const url = currentlyUnfollow
                    ? "api/organizations/unfollow"
                    : "api/organizations/follow";

                try {
                    const response = await fetch("/api/organizations/follow", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        credentials: "include",
                        body: JSON.stringify({organization_id: Number(organizationName)}),
                    });

                    const data = await response.json();
                    if (!response.ok || !data.ok) {
                        alert(data.error || "Failed");
                        return;
                    }
                    
                    button.textContent = currentlyUnfollow ? "Follow" : "Unfollow";
                    button.disabled = true;
                } catch (error) {
                    console.error(error);
                    alert("Network Error");
                }
            };
        });
    }

    function renderOrganizations(organizations) {
        listElements.innerHTML = "";
        if (organizations.length === 0) {
            listElements.textContent = "No Organizations Math These Fields";
            return;
        }

        for (const organization of organizations) {
            const card = document.createElement("div");
            card.className = "card";

            const fields = organization.academic_fields || "Uncategorized";
            const description = organization.organization_description || "";
            
            const isFollowed = organization.followed === 1 || organization.followed === true;

            card.innerHTML = `
                <div class = "card-header">
                    <div class = "card-title>${organization.title}</div>
                    <div class = "card-meta">${fields}</div>
                </div>
                <div class = "card-body>
                    ${description}
                    <div style = "margin-top: 8px;">
                        <button class = "button follow-button" data-organization-name = "${organization.title}">
                            ${isFollowed ? "Unfollow" : "Follow"}
                        </button>
                    </div>
                </div>
            `;
            listElements.appendChild(card);
        }

        attachFollowHandlers();
    }

    filterElements.addEventListener("change", () => {
        const selected = filterElements.value;
        if (!selected) {
            renderOrganizations(allOrganizations);
            return;
        }
        
        const filtered = allOrganizations.filter(organization =>
            (organization.academic_fields || "").split(",").map(element => element.trim()).includes(selected)
        );
    });

    await loadOrganizations();
})