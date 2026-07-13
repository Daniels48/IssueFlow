"use strict";

const container = document.getElementById("projects");

const username = document.getElementById("username");

const logout = document.getElementById("logout");

logout.onclick = async () => {

    await api.post("/auth/logout");

    window.location="/";

};

async function loadUser(){

    const res = await api.get("/auth/me");

    if(!res.ok){

        window.location="/login";

        return;

    }

    const user = await res.json();

    username.textContent=user.username;

}

async function loadProjects(){

    const res = await api.get("/projects");

    if(!res.ok){

        return;

    }
    const projects = await res.json();

    container.innerHTML="";

    for(const project of projects){

        container.innerHTML += `
            <div
                class="project"
                onclick="location='/project/${project.public_id}'"
            >
                <h2>${project.name}</h2>
                <p>${project.description ?? ""}</p>
                <footer>
                    <span>${project.issues_count} issues</span>
                </footer>
            </div>
        `;
    }

}

loadUser();

loadProjects();