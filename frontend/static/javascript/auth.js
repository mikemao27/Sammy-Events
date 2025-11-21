async function refreshAuthUI() {
    const protected_tags = document.querySelectorAll(".protected");
    const loginLink = document.getElementById("login_link");
    const logoutLink = document.getElementById("logout_link");

    try {
        const response = await fetch("/api/user", {
            credentials: "include"
        });

        if (!response.ok) throw new Error("Not Logged In");

        const data = await response.json();
        if (!data.authenticated) throw new Error("Not Logged In");

        protected_tags.forEach(tag => tag.style.display = "inline-flex");
        if (loginLink) loginLink.style.display = "none";
        if (logoutLink) {
            logoutLink.style.display = "inline-flex";
            logoutLink.onclick = async (e) => {
                e.preventDefault();
                await fetch("/api/logout", {
                    method: "POST",
                    credentials: "include"
                });
                window.location.href = "index.html";
            };
        }
    } catch {
        protected_tags.forEach(tag => tag.style.display = "none");
        if (loginLink) loginLink.style.display = "inline-flex";
        if (logoutLink) logoutLink.style.display = "none"
    }
}

document.addEventListener("DOMContentLoaded", refreshAuthUI)
