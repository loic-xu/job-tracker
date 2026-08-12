const API_BASE = "http://localhost:5000/api";

// ── API Layer ──────────────────────────────────────────────────────────

/**
 * Healthcheck ping to verify backend server connectivity.
 */
async function apiHealth() {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
        throw new Error(`Server status: ${response.status}`);
    }
    return await response.json();
}

/**
 * Fetches all tracked job applications from backend.
 */
async function apiGetApplications() {
    const response = await fetch(`${API_BASE}/applications`);
    if (!response.ok) {
        throw new Error(`Failed to fetch applications: ${response.status}`);
    }
    return await response.json();
}

/**
 * Submits a new job application payload to backend.
 * @param {Object} data 
 */
async function apiAddApplication(data) {
    const response = await fetch(`${API_BASE}/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error(`Failed to add application: ${response.status}`);
    }
    return await response.json();
}

/**
 * Partially updates an existing job application.
 * @param {number} id 
 * @param {Object} fields 
 */
async function apiUpdateApplication(id, fields) {
    const response = await fetch(`${API_BASE}/applications/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fields),
    });
    if (!response.ok) {
        throw new Error(`Failed to update application ${id}: ${response.status}`);
    }
    return await response.json();
}

/**
 * Deletes a target application by ID.
 * @param {number} id 
 */
async function apiDeleteApplication(id) {
    const response = await fetch(`${API_BASE}/applications/${id}`, {
        method: "DELETE",
    });
    if (!response.ok) {
        throw new Error(`Failed to delete application ${id}: ${response.status}`);
    }
    return await response.json();
}

/**
 * Fetches application metrics and breakdown statistics.
 */
async function apiGetStats() {
    const response = await fetch(`${API_BASE}/stats`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.status}`);
    }
    return await response.json();
}

// ── UI Rendering ───────────────────────────────────────────────────────

/**
 * Renders the top statistical indicator cards.
 * @param {Object} stats - Stats response containing 'total' and 'by_status'
 */
function renderStats(stats) {
    const totalEl = document.querySelector("#stat-total .stat-value");
    if (totalEl) {
        totalEl.textContent = stats.total || 0;
    }

    const byStatus = stats.by_status || {};
    const statusMap = {
        "stat-a-postuler": "To Apply",
        "stat-postule": "Applied",
        "stat-entretien": "Interview",
        "stat-refus": "Rejected",
        "stat-accepte": "Accepted",
    };

    for (const [elementId, statusKey] of Object.entries(statusMap)) {
        const el = document.querySelector(`#${elementId} .stat-value`);
        if (el) {
            el.textContent = byStatus[statusKey] || 0;
        }
    }

    renderProgressBar(stats);
}

/**
 * Updates relative percentage segment widths in the progress bar.
 * @param {Object} stats 
 */
function renderProgressBar(stats) {
    const total = stats.total || 0;
    const byStatus = stats.by_status || {};

    const statusMap = {
        "progress-a-postuler": "To Apply",
        "progress-postule": "Applied",
        "progress-entretien": "Interview",
        "progress-refus": "Rejected",
        "progress-accepte": "Accepted",
    };

    for (const [elementId, statusKey] of Object.entries(statusMap)) {
        const segmentEl = document.getElementById(elementId);
        if (segmentEl) {
            const count = byStatus[statusKey] || 0;
            const percentage = total > 0 ? (count / total) * 100 : 0;
            segmentEl.style.width = `${percentage}%`;
        }
    }
}

/**
 * Renders connection status pill and footer text indicators.
 * @param {boolean} isConnected 
 */
function renderConnectionStatus(isConnected) {
    const statusBadge = document.getElementById("connection-status");
    const footerStatus = document.getElementById("footer-status");

    if (statusBadge) {
        statusBadge.textContent = isConnected ? "🟢 Connected" : "🔴 Disconnected";
        statusBadge.className = isConnected ? "connected" : "disconnected";
    }

    if (footerStatus) {
        footerStatus.textContent = isConnected
            ? "Server: Online (http://localhost:5000)"
            : "Server: Offline (FastAPI down or CSV locked)";
    }
}

/**
 * Renders application records inside the table body safely using DOM nodes.
 * @param {Array<Object>} applications 
 */
function renderTable(applications) {
    const tbody = document.getElementById("table-body");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!applications || applications.length === 0) {
        const emptyRow = document.createElement("tr");
        const emptyCell = document.createElement("td");
        emptyCell.colSpan = 8;
        emptyCell.className = "empty-state";
        emptyCell.textContent = "No job applications found.";
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
        return;
    }

    const badgeClassMap = {
        "To Apply": "badge-a-postuler",
        "Applied": "badge-postule",
        "Interview": "badge-entretien",
        "Rejected": "badge-refus",
        "Accepted": "badge-accepte",
    };

    applications.forEach((app) => {
        const row = document.createElement("tr");

        // Company
        const cellCompany = document.createElement("td");
        cellCompany.textContent = app.company || "";
        row.appendChild(cellCompany);

        // Title
        const cellTitle = document.createElement("td");
        cellTitle.textContent = app.title || "";
        row.appendChild(cellTitle);

        // Type
        const cellType = document.createElement("td");
        cellType.textContent = app.type || "-";
        row.appendChild(cellType);

        // Date (Interactive Date Input)
        const cellDate = document.createElement("td");
        const dateInput = document.createElement("input");
        dateInput.type = "date";
        dateInput.value = app.application_date || "";
        dateInput.className = "table-date-input";
        dateInput.addEventListener("change", async (e) => {
            const newDate = e.target.value;
            try {
                await apiUpdateApplication(app.id, { application_date: newDate });
                await refreshDashboard();
            } catch (err) {
                console.error(`Failed to update date for app ${app.id}:`, err);
                alert(`Error updating date: ${err.message}`);
            }
        });
        cellDate.appendChild(dateInput);
        row.appendChild(cellDate);

        // Status (Interactive Badge)
        const cellStatus = document.createElement("td");
        const badge = document.createElement("span");
        const currentStatus = app.status || "To Apply";
        badge.className = `badge ${badgeClassMap[currentStatus] || ""}`;
        badge.textContent = currentStatus;
        badge.title = "Click to cycle status";
        badge.addEventListener("click", () => handleStatusCycle(app.id, currentStatus));
        cellStatus.appendChild(badge);
        row.appendChild(cellStatus);

        // Link
        const cellLink = document.createElement("td");
        if (app.link && app.link.trim() !== "") {
            const anchor = document.createElement("a");
            anchor.href = app.link;
            anchor.target = "_blank";
            anchor.rel = "noopener noreferrer";
            anchor.className = "app-link";
            anchor.textContent = "Link 🔗";
            cellLink.appendChild(anchor);
        } else {
            cellLink.textContent = "-";
        }
        row.appendChild(cellLink);

        // Notes
        const cellNotes = document.createElement("td");
        cellNotes.textContent = app.notes || "-";
        cellNotes.title = app.notes || "";
        row.appendChild(cellNotes);

        // Actions (Delete button)
        const cellActions = document.createElement("td");
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn-delete";
        deleteBtn.textContent = "🗑️";
        deleteBtn.title = "Delete application";
        deleteBtn.addEventListener("click", () => handleDelete(app.id));
        cellActions.appendChild(deleteBtn);
        row.appendChild(cellActions);

        tbody.appendChild(row);
    });
}

// ── Event Handlers ─────────────────────────────────────────────────────

/**
 * Handles application creation form submission.
 * @param {Event} event 
 */
async function handleAddSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        company: formData.get("company")?.toString().trim() || "",
        title: formData.get("title")?.toString().trim() || "",
        type: formData.get("type")?.toString().trim() || "",
        application_date: formData.get("application_date")?.toString() || "",
        status: formData.get("status")?.toString() || "To Apply",
        link: formData.get("link")?.toString().trim() || "",
        notes: formData.get("notes")?.toString().trim() || "",
    };

    try {
        await apiAddApplication(payload);
        form.reset();
        setDefaultTodayDate();
        await refreshDashboard();
    } catch (err) {
        console.error("Failed to create application:", err);
        alert(`Error adding application: ${err.message}`);
    }
}

/**
 * Cycles application status to the next logical state when badge is clicked.
 * @param {number} id 
 * @param {string} currentStatus 
 */
async function handleStatusCycle(id, currentStatus) {
    const statusOrder = ["To Apply", "Applied", "Interview", "Rejected", "Accepted"];
    const currentIndex = statusOrder.indexOf(currentStatus);
    const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length];

    try {
        await apiUpdateApplication(id, { status: nextStatus });
        await refreshDashboard();
    } catch (err) {
        console.error(`Failed to update status for app ${id}:`, err);
        alert(`Error updating status: ${err.message}`);
    }
}

/**
 * Confirms and executes application deletion.
 * @param {number} id 
 */
async function handleDelete(id) {
    if (!confirm("Are you sure you want to delete this job application?")) {
        return;
    }

    try {
        await apiDeleteApplication(id);
        await refreshDashboard();
    } catch (err) {
        console.error(`Failed to delete application ${id}:`, err);
        alert(`Error deleting application: ${err.message}`);
    }
}

/**
 * Fetches fresh metrics and list data to refresh the entire UI.
 */
async function refreshDashboard() {
    try {
        const [stats, applications] = await Promise.all([
            apiGetStats(),
            apiGetApplications(),
        ]);

        renderConnectionStatus(true);
        renderStats(stats);
        renderTable(applications);
    } catch (err) {
        console.error("Failed to refresh dashboard:", err);
        renderConnectionStatus(false);
    }
}

// ── Lifecycle Initialization ───────────────────────────────────────────

/**
 * Auto-populates the Job Link input field with the active browser tab URL.
 */
async function autoPopulateActiveTabUrl() {
    const linkInput = document.getElementById("input-link");
    if (!linkInput) return;

    try {
        if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.query) {
            const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (activeTab && activeTab.url && !activeTab.url.startsWith("chrome://")) {
                linkInput.value = activeTab.url;
            }
        }
    } catch (err) {
        console.error("Failed to query active tab URL:", err);
    }
}

/**
 * Sets the date input field default value to today (YYYY-MM-DD).
 */
function setDefaultTodayDate() {
    const dateInput = document.getElementById("input-date");
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.value = today;
    }
}

/**
 * Extension popup lifecycle initialization entry point.
 */
async function init() {
    const addForm = document.getElementById("add-form");
    if (addForm) {
        addForm.addEventListener("submit", handleAddSubmit);
    }

    setDefaultTodayDate();
    await autoPopulateActiveTabUrl();
    await refreshDashboard();
}

document.addEventListener("DOMContentLoaded", init);
