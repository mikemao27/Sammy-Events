document.addEventListener("DOMContentLoaded", () => {
    loadDegreeCheckboxes();
    setupSignupForm();
});

async function loadDegreeCheckboxes() {
    const container = document.getElementById("degrees-container");
    if (!container) return;

    try {
        const response = await fetch("/api/academic-fields", { credentials: "include" });
        if (!response.ok) {
            container.textContent = "Could Not Load Academic Fields";
            return;
        }

        const fields = await response.json();

        container.innerHTML = "";
        fields.forEach(field => {
            const wrapper = document.createElement("label");
            wrapper.style.display = "block";
            wrapper.style.marginBottom = "4px";

            const cb = document.createElement("input");
            cb.type = "checkbox";
            cb.value = field.id;
            cb.name = "degree";

            wrapper.appendChild(cb);
            wrapper.appendChild(document.createTextNode(" " + (field.name || field.degree_name)));
            container.appendChild(wrapper);
        });
    } catch (error) {
        console.error("Error Loading Academic Fields", error);
        container.textContent = "Error loading academic fields.";
    }
}

function setupSignupForm() {
    const form = document.getElementById("signup-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const first_name = document.getElementById("first_name").value.trim();
        const last_name = document.getElementById("last_name").value.trim();
        const netID = document.getElementById("netID").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone_number = document.getElementById("phone_number").value.trim();
        const password = document.getElementById("password").value;

        const degree_ids = Array.from(
            document.querySelectorAll('#degrees-container input[type = "checkbox"]:checked')
        ).map(cb => Number(cb.value));

        try {
            const response = await fetch("/api/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    first_name,
                    last_name,
                    netID,
                    email,
                    password,
                    phone_number,
                    degree_ids,
                }),
            });

            const data = await response.json();
            if (!response.ok || data.ok === false) {
                alert(data.error || "Sign Up Failed");
                return;
            }

            alert("Account Created! Please Log In");
            window.location.href = "login.html";
        } catch (error) {
            console.error("Error signing up: ", error);
            alert("Network Error");
        }
    });
}
