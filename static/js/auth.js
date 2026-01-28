console.log("auth.js loaded");


document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("loginForm");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); 

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/api/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Invalid credentials");
            }

            localStorage.setItem("access_token", data.token.access);
            localStorage.setItem("refresh_token", data.token.refresh);

            // redirect
            window.location.href = "/api/chat/";
        } catch (error) {
            document.getElementById("error").innerText = error.message;
        }
    });
});
async function authFetch(url, options = {}) {
  let accessToken = localStorage.getItem("access_token");

  options.headers = {
    ...options.headers,
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  };

  let response = await fetch(url, options);

  // If access token expired → refresh it
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();

    if (refreshed) {
      accessToken = localStorage.getItem("access_token");

      options.headers.Authorization = `Bearer ${accessToken}`;
      response = await fetch(url, options);
    }
  }

  return response;
}
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");

  if (!refreshToken) return false;

  try {
    const response = await fetch("api/token/refresh/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      logoutUser();
      return false;
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access);
    return true;
  } catch {
    logoutUser();
    return false;
  }
}
function logoutUser() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/";
}
function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}