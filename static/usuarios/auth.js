const state = {
    token: localStorage.getItem("zuren_session") || "",
    profile: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

async function api(path, options = {}) {
    const headers = { "Content-Type": "application/json", ...options.headers };
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    const response = await fetch(path, { ...options, headers });
    const data = response.status === 204 ? {} : await response.json().catch(() => ({}));
    if (!response.ok) {
        const detail = Array.isArray(data.error)
            ? data.error.join(" ")
            : data.error || Object.values(data).flat().join(" ") || "No se pudo completar la solicitud.";
        if (response.status === 401 && state.token) clearSession();
        throw new Error(detail);
    }
    return data;
}

function formData(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function setBusy(form, busy) {
    form.querySelectorAll("button, input").forEach((control) => {
        control.disabled = busy;
    });
}

function showMessage(target, text, success = false) {
    target.textContent = text;
    target.classList.remove("hidden", "success");
    if (success) target.classList.add("success");
}

function clearMessage(target) {
    target.textContent = "";
    target.classList.add("hidden");
    target.classList.remove("success");
}

function setAuthMode(mode) {
    const login = mode === "login";
    $("#login-form").classList.toggle("hidden", !login);
    $("#register-form").classList.toggle("hidden", login);
    $("#login-tab").classList.toggle("active", login);
    $("#register-tab").classList.toggle("active", !login);
    $("#login-tab").setAttribute("aria-selected", String(login));
    $("#register-tab").setAttribute("aria-selected", String(!login));
    $("#auth-title").textContent = login ? "Bienvenido de nuevo" : "Crea tu cuenta";
    $("#auth-subtitle").textContent = login
        ? "Ingresa tus credenciales para continuar."
        : "Registra tus datos para acceder como cliente.";
    clearMessage($("#auth-message"));
}

function clearSession() {
    state.token = "";
    state.profile = null;
    localStorage.removeItem("zuren_session");
    $("#account-view").classList.add("hidden");
    $("#auth-view").classList.remove("hidden");
}

function initials(name) {
    return name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function renderProfile(profile) {
    state.profile = profile;
    $("#auth-view").classList.add("hidden");
    $("#account-view").classList.remove("hidden");
    $("#welcome-name").textContent = `Hola, ${profile.nombre.split(" ")[0]}`;
    $("#profile-name").textContent = profile.nombre;
    $("#profile-identity").textContent = `${profile.username} · ${profile.email}`;
    $("#profile-role").textContent = profile.rol_nombre;
    $("#user-initials").textContent = initials(profile.nombre);
    $("#profile-form").elements.nombre.value = profile.nombre;
    $("#profile-form").elements.email.value = profile.email;
    $("#profile-form").elements.username.value = profile.username;
    $("#profile-form").elements.rol.value = profile.rol_nombre;
    const isAdmin = profile.rol_nombre.toLowerCase() === "administrador";
    $$(".admin-only").forEach((element) => element.classList.toggle("hidden", !isAdmin));
}

async function loadProfile() {
    if (!state.token) return;
    try {
        renderProfile(await api("/api/auth/perfil/"));
    } catch {
        clearSession();
        showMessage($("#auth-message"), "Tu sesion finalizo. Ingresa nuevamente.");
    }
}

async function loadUsers() {
    const body = $("#users-table");
    body.innerHTML = '<tr><td colspan="4">Cargando usuarios...</td></tr>';
    try {
        const data = await api("/api/usuarios/");
        const users = data.results || data;
        body.innerHTML = users.map((user) => `
            <tr>
                <td class="user-cell"><strong>${escapeHtml(user.nombre)}</strong><small>${escapeHtml(user.email)}</small></td>
                <td>${escapeHtml(user.rol_nombre)}</td>
                <td><span class="status ${user.estado}">${escapeHtml(user.estado)}</span></td>
                <td>${user.id === state.profile.id
                    ? '<span class="status">Tu cuenta</span>'
                    : `<button class="secondary-button row-action" data-user="${user.id}" data-action="${user.estado === "activo" ? "desactivar" : "activar"}">${user.estado === "activo" ? "Desactivar" : "Activar"}</button>`
                }</td>
            </tr>
        `).join("") || '<tr><td colspan="4">No hay usuarios registrados.</td></tr>';
    } catch (error) {
        body.innerHTML = `<tr><td colspan="4">${escapeHtml(error.message)}</td></tr>`;
    }
}

async function loadRoles() {
    const select = $("#admin-user-form").elements.rol_id;
    const data = await api("/api/roles/");
    const roles = data.results || data;
    select.innerHTML = '<option value="">Selecciona un rol</option>' + roles
        .map((role) => `<option value="${role.id}">${escapeHtml(role.nombre)}</option>`)
        .join("");
}

function escapeHtml(value) {
    const node = document.createElement("span");
    node.textContent = value ?? "";
    return node.innerHTML;
}

$("#login-tab").addEventListener("click", () => setAuthMode("login"));
$("#register-tab").addEventListener("click", () => setAuthMode("register"));

$$(".reveal").forEach((button) => {
    button.addEventListener("click", () => {
        const input = button.previousElementSibling;
        input.type = input.type === "password" ? "text" : "password";
        button.setAttribute("aria-label", input.type === "password" ? "Mostrar contrasena" : "Ocultar contrasena");
    });
});

$("#login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formData(form);
    clearMessage($("#auth-message"));
    setBusy(form, true);
    try {
        const result = await api("/api/auth/login/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        state.token = result.token;
        localStorage.setItem("zuren_session", state.token);
        await loadProfile();
        form.reset();
    } catch (error) {
        showMessage($("#auth-message"), error.message);
    } finally {
        setBusy(form, false);
    }
});

$("#register-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formData(form);
    clearMessage($("#auth-message"));
    setBusy(form, true);
    try {
        await api("/api/auth/registro/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        form.reset();
        setAuthMode("login");
        showMessage($("#auth-message"), "Cuenta creada. Ya puedes iniciar sesion.", true);
    } catch (error) {
        showMessage($("#auth-message"), error.message);
    } finally {
        setBusy(form, false);
    }
});

$("#logout-button").addEventListener("click", async () => {
    try {
        await api("/api/auth/logout/", { method: "POST", body: "{}" });
    } finally {
        clearSession();
    }
});

$$(".section-tab").forEach((button) => {
    button.addEventListener("click", () => {
        $$(".section-tab").forEach((tab) => tab.classList.remove("active"));
        $$(".account-section").forEach((section) => section.classList.add("hidden"));
        button.classList.add("active");
        $(`#${button.dataset.section}`).classList.remove("hidden");
        clearMessage($("#account-message"));
        if (button.dataset.section === "users-section") {
            Promise.all([loadUsers(), loadRoles()]).catch((error) => {
                showMessage($("#account-message"), error.message);
            });
        }
    });
});

$("#profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
        nombre: form.elements.nombre.value,
        email: form.elements.email.value,
    };
    setBusy(form, true);
    try {
        const profile = await api("/api/auth/perfil/", {
            method: "PATCH",
            body: JSON.stringify(payload),
        });
        renderProfile(profile);
        showMessage($("#account-message"), "Perfil actualizado correctamente.", true);
    } catch (error) {
        showMessage($("#account-message"), error.message);
    } finally {
        setBusy(form, false);
    }
});

$("#password-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formData(form);
    setBusy(form, true);
    try {
        const result = await api("/api/auth/cambiar-password/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        form.reset();
        showMessage($("#account-message"), result.mensaje, true);
    } catch (error) {
        showMessage($("#account-message"), error.message);
    } finally {
        setBusy(form, false);
    }
});

$("#close-sessions-button").addEventListener("click", async () => {
    try {
        const result = await api("/api/auth/cerrar-otras-sesiones/", {
            method: "POST",
            body: "{}",
        });
        showMessage($("#account-message"), result.mensaje, true);
    } catch (error) {
        showMessage($("#account-message"), error.message);
    }
});

$("#refresh-users-button").addEventListener("click", loadUsers);
$("#admin-user-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formData(form);
    setBusy(form, true);
    try {
        await api("/api/usuarios/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        form.reset();
        form.closest("details").removeAttribute("open");
        await loadUsers();
        showMessage($("#account-message"), "Usuario creado correctamente.", true);
    } catch (error) {
        showMessage($("#account-message"), error.message);
    } finally {
        setBusy(form, false);
    }
});

$("#users-table").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-user]");
    if (!button) return;
    button.disabled = true;
    try {
        await api(`/api/usuarios/${button.dataset.user}/${button.dataset.action}/`, {
            method: "POST",
            body: "{}",
        });
        await loadUsers();
    } catch (error) {
        showMessage($("#account-message"), error.message);
        button.disabled = false;
    }
});

loadProfile();
