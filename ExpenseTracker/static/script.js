// Expense Tracker — JavaScript Utilities
// ========================================
// Minimal, dependency-free JS for UX enhancements only.
// All business logic lives in Flask/Python.

document.addEventListener("DOMContentLoaded", function () {

  // ── Auto-dismiss flash alerts after 5 seconds ──────────────────────────────
  const alerts = document.querySelectorAll(".alert-auto-dismiss");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";
      setTimeout(function () {
        if (alert.parentNode) alert.parentNode.removeChild(alert);
      }, 500);
    }, 5000);
  });

  // ── Delete confirmation dialog ─────────────────────────────────────────────
  const deleteForms = document.querySelectorAll(".delete-form");
  deleteForms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const title = form.dataset.title || "this expense";
      if (!confirm("Are you sure you want to delete \"" + title + "\"?\nThis action cannot be undone.")) {
        e.preventDefault();
      }
    });
  });

  // ── Set today's date as default on Add Expense form ────────────────────────
  const dateInput = document.getElementById("expense_date");
  if (dateInput && !dateInput.value) {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, "0");
    const dd = String(today.getDate()).padStart(2, "0");
    dateInput.value = yyyy + "-" + mm + "-" + dd;
  }

  // ── Amount field: allow only valid decimal input ───────────────────────────
  const amountInput = document.getElementById("amount");
  if (amountInput) {
    amountInput.addEventListener("input", function () {
      const val = this.value;
      if (val !== "" && (isNaN(parseFloat(val)) || parseFloat(val) <= 0)) {
        this.classList.add("input-error");
      } else {
        this.classList.remove("input-error");
      }
    });
  }

  // ── Budget progress bar live colour update ─────────────────────────────────
  const progressBar = document.getElementById("budget-progress-bar");
  if (progressBar) {
    const pct = parseFloat(progressBar.dataset.pct || "0");
    if (pct >= 100) {
      progressBar.classList.add("over-budget");
    } else if (pct >= 80) {
      progressBar.classList.add("near-budget");
    }
  }

  // ── Highlight the active nav link ──────────────────────────────────────────
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach(function (link) {
    const href = link.getAttribute("href");
    if (href && currentPath === href) {
      link.classList.add("active");
    } else if (href && href !== "/" && currentPath.startsWith(href)) {
      link.classList.add("active");
    }
  });

  // ── Search form: submit on Enter key ──────────────────────────────────────
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        const form = searchInput.closest("form");
        if (form) form.submit();
      }
    });
  }

});
