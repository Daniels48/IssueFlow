document.addEventListener("DOMContentLoaded", async () => {
    const nav = document.getElementById("nav");
    const res = await api.post("/api/users/me");

    if (!res || !res.ok) {
        nav.innerHTML = `
            <a href="/login">Login</a>
            <a href="/register" class="btn primary">Register</a>
        `;
        return;
    }

    const user = await res.json();
    nav.innerHTML = `
        <span class="username">${user.username}</span>
        <a href="/projects">Projects</a>
        <button id="logout" class="btn primary">Logout</button>
    `;

    document.getElementById("logout").addEventListener("click", logout);

});