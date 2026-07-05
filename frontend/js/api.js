// ---------- Config ----------
const API_BASE = "http://localhost:8000";
const APP_TIMEZONE = "America/New_York";

function formatNYC(iso) {
  if (!iso) return "—";

  return new Intl.DateTimeFormat("en-US", {
    timeZone: APP_TIMEZONE,
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(iso));
}

// NYC "now" → datetime-local input value
function nowAsNYCDateTimeLocalValue() {
  const now = new Date();

  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: APP_TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(now);

  const get = (t) => parts.find((p) => p.type === t).value;

  return `${get("year")}-${get("month")}-${get("day")}T${get("hour")}:${get("minute")}`;
}

// ---------- Fetch helpers ----------
async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  return handleResponse(res);
}

async function apiPost(path, body, isFormData = false) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: isFormData ? undefined : { "Content-Type": "application/json" },
    body: isFormData ? body : JSON.stringify(body),
  });

  return handleResponse(res);
}

async function handleResponse(res) {
  let data;

  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const message =
      (data && (data.detail || data.message)) ||
      `Request failed (${res.status})`;

    throw new Error(message);
  }

  return data;
}

// ---------- Utils ----------
function fmtNum(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString();
}